"""Semantic Kernel integration and deterministic LLM adapter for ThesisForge AI."""

from __future__ import annotations
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional
import semantic_kernel as sk
from semantic_kernel.kernel import Kernel

_pkg_root = str(Path(__file__).resolve().parent.parent)
if _pkg_root not in sys.path:
    sys.path.insert(0, _pkg_root)


class LLMServiceAdapter:
    """Manages Semantic Kernel initialization, plugins, and model invocation.

    Supports live LLM (OpenAI / Azure OpenAI) via Semantic Kernel when credentials exist,
    or deterministic mode for reproducible evaluation and testing (SRS Section 3.4 & 14).
    """

    def __init__(self):
        self.provider = os.getenv("LLM_PROVIDER", "mock").lower()
        self.api_key = os.getenv("LLM_API_KEY", "")
        self.model = os.getenv("LLM_MODEL", "gpt-4o-mini")
        self.kernel = Kernel()

        self.is_live = False
        if self.provider in ("openai", "azure_openai") and self.api_key:
            try:
                if self.provider == "openai":
                    from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
                    chat_service = OpenAIChatCompletion(
                        ai_model_id=self.model,
                        api_key=self.api_key,
                    )
                    self.kernel.add_service(chat_service)
                    self.is_live = True
                elif self.provider == "azure_openai":
                    from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
                    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "")
                    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
                    chat_service = AzureChatCompletion(
                        deployment_name=self.model,
                        endpoint=endpoint,
                        api_key=self.api_key,
                        api_version=api_version,
                    )
                    self.kernel.add_service(chat_service)
                    self.is_live = True
            except Exception as e:
                print(f"[Warning] Failed to initialize live Semantic Kernel provider {self.provider}: {e}. Falling back to deterministic mode.")
                self.is_live = False

    def get_kernel(self) -> Kernel:
        return self.kernel

    def is_live_mode(self) -> bool:
        return self.is_live
