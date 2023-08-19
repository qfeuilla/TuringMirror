import logging
from io import StringIO

from interlab import lang_models
from langchain.chat_models import ChatAnthropic, ChatOpenAI
from tenacity import retry, wait_random_exponential


def get_engine(model: str, kwargs: dict):
    if model.startswith("gpt"):
        return ChatOpenAI(model_name=model, **kwargs)
    if model.startswith("claude"):
        return ChatAnthropic(model=model, **kwargs)
    raise ValueError(f"Unknown model name: {model}")


@retry(wait=wait_random_exponential(multiplier=5, max=60))
def query_model(*args, **kwargs):
    # add logging handler for calls to lang_models.query_model
    # (this is a hack to get the logs from lang_models.query_model)
    # and redirect to StringBuffer
    logger = logging.getLogger("openai")
    logger.setLevel(logging.INFO)
    log_capture_string = StringIO()
    handler = logging.StreamHandler(log_capture_string)
    logger.addHandler(handler)
    result = lang_models.query_model(*args, **kwargs)
    log_contents = log_capture_string.getvalue()
    if "rate_limit_exceeded" in log_contents.lower():
        log_capture_string.close()
        raise Exception(log_contents)
    log_capture_string.close()
    return result
