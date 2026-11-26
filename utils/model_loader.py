import os
from typing import Literal, Optional

from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, ConfigDict, Field

from exception.exceptionhandling import ConfigurationError
from logger.logging import get_logger
from utils.config_loader import load_config

logger = get_logger(__name__)


class ConfigLoader:
    """Loads the configuration for the project."""

    def __init__(self):
        self.config = load_config()
        logger.debug("Loaded LLM configuration from config.yaml")

    def __getitem__(self, key):
        return self.config[key]


class ModelLoader(BaseModel):
    """Handles loading of LLM models from different providers."""

    model_config = ConfigDict(arbitrary_types_allowed=True)

    model_provider: Literal["groq", "openai"] = "groq"
    config: Optional[ConfigLoader] = Field(default=None, exclude=True)

    def __init__(self, **data):
        super().__init__(**data)
        if self.config is None:
            self.config = ConfigLoader()

    def load_llm(self):
        """Load and return the LLM model based on the configured provider."""
        if self.model_provider == "groq":
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ConfigurationError("GROQ_API_KEY not found in environment variables.")
            model_name = self.config["llm"]["groq"]["model_name"]
            logger.info("Initializing Groq model: %s", model_name)
            return ChatGroq(model=model_name, api_key=groq_api_key)

        if self.model_provider == "openai":
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ConfigurationError("OPENAI_API_KEY not found in environment variables.")
            model_name = self.config["llm"]["openai"]["model_name"]
            logger.info("Initializing OpenAI model: %s", model_name)
            return ChatOpenAI(model_name=model_name, api_key=openai_api_key)

        raise ConfigurationError(f"Unsupported model provider: {self.model_provider}")
