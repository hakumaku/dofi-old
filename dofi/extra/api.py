from .abc import API
from .github.api import GithubAPI as Github

__all__ = ["Github", "API"]
