from langchain.chat_models import ChatAnthropic, ChatOpenAI


def get_engine(model: str, kwargs: dict):
    if model.startswith("gpt"):
        return ChatOpenAI(model_name=model, **kwargs)
    if model.startswith("claude"):
        return ChatAnthropic(model=model, **kwargs)
    raise ValueError(f"Unknown model name: {model}")
