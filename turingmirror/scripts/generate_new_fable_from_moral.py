"""Uses an LLM to generate a new fable from a moral."""
import json
import logging
from pathlib import Path
from typing import Optional

import hydra
from hydra.utils import to_absolute_path
from interlab.context import Context, FileStorage
from interlab.lang_models import query_model
from interlab.queries import find_and_parse_json_block
from omegaconf import DictConfig, OmegaConf
from tqdm import tqdm

from turingmirror.utils.log import log_exceptions
from turingmirror.utils.model import get_engine

LOGGER = logging.getLogger(__name__)


def fable_prompt(moral: str) -> str:
    return f"Can you write a very short fable (less than 10 sentences) whose moral is \"{moral}\"? Do not explicitly state the moral."


def fable_extraction(fable: str) -> str:
    return f"Here is a text containing a fable:\n{fable}\nCopy the contained fable in json with the key \"fable\" and the value being the fable. Don't talk, only give me the json."


@hydra.main(
    version_base="1.2",
    config_path="conf",
    config_name="generate_new_fable_from_moral",
)
@log_exceptions(LOGGER)
def main(cfg: DictConfig):
    storage = FileStorage(Path.cwd())  # for storing contexts (structured logs)
    LOGGER.info(storage.directory)

    ids = cfg.ids or []
    if not isinstance(ids, list):
        ids = [ids]

    # load json lines data
    data_path = to_absolute_path(cfg.data)
    data = []
    with open(data_path, "r") as f:
        for line in f:
            d = json.loads(line)
            if ids and d["id"] not in ids:
                continue
            data.append(d)

    model = get_engine(
        model=cfg.model.name,
        kwargs=cfg.model.kwargs or {},
    )

    extraction_model = get_engine(
        model="gpt-3.5-turbo",
        kwargs={"temperature": 0.7},
    )

    cfg_dict = OmegaConf.to_container(cfg, resolve=True)
    with Context(
            "generate_new_fable_from_moral",
            storage=storage,
            inputs=cfg_dict,
    ) as c:
        output = []
        for d in tqdm(data):
            id = d["id"]
            moral = d["moral"]
            if extracted_fable := generate_new_fable(
                    id=id,
                    moral=moral,
                    extraction_model=extraction_model,
                    model=model
            ):
                d_out = {
                    "id": id,
                    "fable": extracted_fable,
                    "moral": moral,
                }
                output.append(d_out)
                with open("fables.jsonl", "a") as f:
                    f.write(json.dumps(d_out))
                    f.write("\n")

        c.set_result(output)


@log_exceptions(LOGGER)
def generate_new_fable(id: int, moral: str, extraction_model, model) -> Optional[str]:
    try:
        generation_prompt = fable_prompt(moral)
        raw_fable = query_model(model=model, prompt=generation_prompt)
        extraction_prompt = fable_extraction(raw_fable)
        extracted_fable_json = query_model(
            model=extraction_model,
            prompt=extraction_prompt,
        )
        return find_and_parse_json_block(extracted_fable_json)["fable"]
    except Exception as e:
        LOGGER.exception(f"id: {id}, exception: {e}")


if __name__ == '__main__':
    main()
