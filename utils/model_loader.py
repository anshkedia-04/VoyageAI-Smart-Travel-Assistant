import os
from typing import Literal, Optional, Any
from pydantic import BaseModel, Field
from utils.config_loader import load_config
from langchain_groq import ChatGroq
from langchain_openai import ChatOpenAI


class ConfigLoader:
    """Loads the configuration for the project."""
    def __init__(self):
        print("Loaded config...")
        self.config = load_config()

    def __getitem__(self, key):
        return self.config[key]


class ModelLoader(BaseModel):
    """Handles loading of LLM models from different providers."""
    model_provider: Literal["groq", "openai"] = "groq"
    config: Optional[ConfigLoader] = Field(default=None, exclude=True)

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **data):
        super().__init__(**data)
        if self.config is None:
            self.config = ConfigLoader()

    def load_llm(self):
        """Load and return the LLM model based on the provider."""
        print("LLM loading...")
        print(f"Loading model from provider: {self.model_provider}")

        if self.model_provider == "groq":
            print("Loading LLM from Groq...")
            groq_api_key = os.getenv("GROQ_API_KEY")
            if not groq_api_key:
                raise ValueError("GROQ_API_KEY not found in environment variables!")

            # Make sure your config has the updated supported model
            model_name = self.config["llm"]["groq"]["model_name"]
            llm = ChatGroq(model=model_name, api_key=groq_api_key)

        elif self.model_provider == "openai":
            print("Loading LLM from OpenAI...")
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if not openai_api_key:
                raise ValueError("OPENAI_API_KEY not found in environment variables!")

            # Use model name from config
            model_name = self.config["llm"]["openai"]["model_name"]
            llm = ChatOpenAI(model_name=model_name, api_key=openai_api_key)

        else:
            raise ValueError(f"Unsupported model provider: {self.model_provider}")

        print(f"Loaded model: {llm}")
        return llm
