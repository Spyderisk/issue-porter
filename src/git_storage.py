from typing import IO, Any
from git import Repo
import os
import json
import tomllib

ROOT = "storage_repo/.issue-porter"
VERSION = (0, 1, 0)

def fopen(path: str, mode: str) -> IO[Any]:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return open(path, mode=mode)

class PersistentStorage:
    repo: Repo

    version: tuple[int, int, int]

    @classmethod
    def deserialize(cls) -> "PersistentStorage":
        self = cls()

        obj = json.load(fopen(f"{ROOT}/issue-porter.json", mode="r"))

        self.version = obj["version"]

        return self

    @classmethod
    def default(cls) -> "PersistentStorage":
        self = cls()

        self.version = VERSION

        return self

    def serialize(self):
        print("Saving persistent data")
        json.dump({
            "version": self.version
        }, fopen(f"{ROOT}/issue-porter.json", mode="w"))

    @classmethod
    def load_or_create_config(cls, repo: Repo) -> "PersistentStorage":
        if os.path.exists(f"{ROOT}/issue-porter.json"):
            print("Loaded persistent data")
            return cls.deserialize()
        else:
            print("Generated new persistent data")
            return cls.default()
        
    def gen_mapping(self, c: dict):
        with fopen(f"{ROOT}/user_mapping.toml", "w") as f:
            f.write(
"""
[user-mapping]
# Behaviour for non-mapped users
# Options:
#   "keep"   - Don't attempt mapping, this may ping randoms unintentionally
#   "remove" - Replace with value of user-mapping.missing-user-message
missing-user-behavior = "keep"
missing-user-message = "[USER REMOVED]"

[[user]]
gitlab-username = "@username"
github-username = "@username"

# Add more users like so
# [[user]]
# gitlab-username: "@username"
# github-username: "@username"
"""
            )

    def load_user_mapping(self) -> dict[str, list[dict[str, str]] | dict[str, str]]:
        with fopen(f"{ROOT}/user_mapping.toml", "r") as f:
            return tomllib.loads(f.read())



def load_repo(c: dict) -> PersistentStorage:
    repo: Repo

    # Repo may already exist from previous runs
    if os.path.exists("storage_repo/.git/"):
        repo = Repo("storage_repo")
    else:
        repo = Repo.clone_from(
            f"https://github.com/{c["github"]["storage_repo"]}.git", "storage_repo")

    return PersistentStorage.load_or_create_config(repo)
