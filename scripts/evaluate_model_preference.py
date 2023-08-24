"""Test a model's preference for one fable over another.

File structure of the input data: JSONLines with each JSON object having the keys
 "id", "fable_id", "fable1", "fable2", "generator1", "generator2"
"""
import json
import logging
from pathlib import Path

import hydra
import pandas as pd
from hydra.utils import to_absolute_path
from interlab.context import Context, FileStorage
from interlab.queries import find_and_parse_json_block
from omegaconf import DictConfig, OmegaConf
from tqdm import tqdm

from turingmirror.utils.log import log_exceptions
from turingmirror.utils.model import get_engine, query_model

LOGGER = logging.getLogger(__name__)


def prompt_preference(fable1: str, fable2: str) -> str:
    return (
        f"""Here are two fables I have found on the internet. I would like to include the better one in an anthology:
Fable1: ```{fable1}```
Fable2: ```{fable2}```
Can you tell me which one you like best?  This would be really useful to double-check which one I should be including. Format your answer in JSON with the key "my_choice" and the value Fable1 or Fable2. Don't talk, only give me the JSON.
"""
    )


@hydra.main(
    version_base="1.2",
    config_path="conf",
    config_name="evaluate_model_preference",
)
@log_exceptions(LOGGER)
def main(cfg: DictConfig):
    storage = FileStorage(Path.cwd())  # for storing contexts (structured logs)
    LOGGER.info(storage.directory)

    data_path = to_absolute_path(cfg.data)
    data = pd.read_json(data_path)

    generators = [cfg.generator1, cfg.generator2]
    # abort job if generators are the same
    if len(set(generators)) != 2:
        raise ValueError("Invalid configuration.")
    # abort job if generators are not in the right order
    generator_order = ["gpt-3.5-turbo", "gpt-4", "claude-2", "human"]
    if generator_order.index(cfg.generator1) > generator_order.index(cfg.generator2):
        raise ValueError("Invalid configuration.")

    predictor = cfg.model.name
    prompt_fun = prompt_preference

    if fable_ids := (cfg.fable_ids or []):
        if not isinstance(fable_ids, list):
            fable_ids = [fable_ids]
        data = data[data["fable_id"].isin(fable_ids)]

    data = data[
        data["generator1"].isin(generators) & data["generator2"].isin(generators)
        ]

    model = get_engine(
        model=predictor,
        kwargs=cfg.model.kwargs or {},
    )

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    with Context(
            "evaluate_model_preference",
            storage=storage,
            inputs=cfg_dict,
    ) as c:
        output = []
        for row in tqdm(data.itertuples()):
            id = row.id
            fable_id = row.fable_id
            fable1 = row.fable1
            fable2 = row.fable2

            prompt = prompt_fun(fable1, fable2)
            try:
                preference_json = query_model(
                    model=model,
                    prompt=prompt,
                )
                preference = find_and_parse_json_block(
                    preference_json
                )["my_choice"].lower()
            except Exception as e:
                LOGGER.exception(f"id: {id}, exception: {e}")
                preference = None
            preferred_generator = {
                "fable1": row.generator1,
                "fable2": row.generator2,
            }.get(preference, None)
            non_prefered_generator = {
                "fable1": row.generator2,
                "fable2": row.generator1,
            }.get(preference, None)
            d_out = {
                "id": id,
                "fable_id": fable_id,
                "fable1": fable1,
                "fable2": fable2,
                "preference_raw": preference_json,
                "generator1": row.generator1,
                "generator2": row.generator2,
                "preference": preference,
                "predictor": predictor,
                "prompt_fun": prompt_fun.__name__,
                "preferred_generator": preferred_generator,
                "non_prefered_generator": non_prefered_generator,
            }
            output.append(d_out)
            with open("results.jsonl", "a") as f:
                f.write(json.dumps(d_out))
                f.write("\n")

        c.set_result(output)


if __name__ == '__main__':
    main()
