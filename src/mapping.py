# Copyright 2023 The Spyderisk Authors

#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at:

#        http://www.apache.org/licenses/LICENSE-2.0

#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

# <!-- SPDX-License-Identifier: Apache 2.0 -->
# <!-- SPDX-FileCopyrightText: 2023 The Spyderisk Authors -->
# <!-- SPDX-ArtifactOfProjectName: Spyderisk -->
# <!-- SPDX-FileType: Source code -->
# <!-- SPDX-FileComment: Original by Jacob Lewis, November 2023 -->

# Strucutre for managing the mapping between gitlab and github links

from issue import GithubID, GitlabID, GitlabIID, Issue, Comment
from git_storage import PersistentStorage as PS
from gitlab import download_file

from multiprocessing import Process

# Using a bidict so I can map back and forward
from bidict import bidict
from enum import Enum
import re

class DualDict[L, R, V]:
    l: bidict[L, V]
    r: bidict[R, V]

    def __init__(self) -> None:
        l = {}
        r = {}

    def push(self, l: L, r: R, v: V):
        self.l[l] = v
        self.r[r] = v

    def get_l(self, k: L) -> V:
        return self.l[k]

    def get_r(self, k: R) -> V:
        return self.r[k]
    
    def inverse(self, k: V) -> tuple[L, R]:
        return (
            self.l.inverse[k],
            self.r.inverse[k]
        )


class Mapping:
    repo: tuple[str, str]
    issues: bidict[GitlabIID, GithubID]
    comments: bidict[GitlabID, GithubID]
    user: dict[str, str]

    def __init__(self, gitlab_target: str, github_target: str) -> None:
        self.repo = (gitlab_target, github_target)
        self.issues = bidict()
        self.comments = bidict()
        self.user = {}


    def collect_ids(self, issues: list[Issue]):
        for i in issues:
            self.issues[i.meta.ids.gitlab_internal] = i.meta.ids.github # type: ignore
            for thread in i.threads:
                for c in thread:
                    self.comments[c.meta.ids.gitlab] = c.meta.ids.github
    
    def init_persistent_mapping(self, c: dict, ps: PS):
        obj = ps.load_user_mapping()

        c["user-mapping"] = obj["user-mapping"] # Add additional settings

        for user in obj["user"]:
            self.user[user["gitlab-username"]] = user["github-username"] # type: ignore


class URLType(Enum):
    Misc = 0
    UnknownGitlab = 1
    Repo = 2
    Issue = 3
    Comment = 4

class URL:
    kind: URLType
    url: list[str]
    # We do not need to store the path, as we ignore repos outside of the target one
    #             Issue      # Issue comment
    extra: None | GitlabID | tuple[GitlabID, GitlabIID]

    def __init__(self, url: str, c: dict) -> None:
        split = url \
            .lstrip("https://") \
            .lstrip("http://") \
            .split("/")

        self.url = split

        if self.url[0] == c["gitlab"]["domain"]: # If gitlab
            path: list[str] = c["gitlab"]["repo_path"].split("/")

            if self.url[1:1 + len(path)] == path: # If target repo
                if self.url[-3:-1] == ["-", "issues"]:
                    if '#' in self.url[-1]:
                        self.kind = URLType.Comment
                        self.extra = (
                            GitlabID(self.url[-1].split("#")[0]),
                            GitlabID(self.url[-1].split("_")[-1])
                        ) # Get note + issue ID
                    else: 
                        self.kind = URLType.Issue
                        self.extra = GitlabID(self.url[-1]) # Get issue ID
                else:
                    self.kind = URLType.Repo
            else:
                self.kind = URLType.UnknownGitlab
        else:
            self.kind = URLType.Misc

    def remap(self, c: dict, m: Mapping) -> str:
        match self.kind:
            case URLType.Misc:
                return f"https://{"/".join(self.url)}"

            case URLType.UnknownGitlab:
                return "[INTERNAL LINK REMOVED]"
            
            case URLType.Repo:
                return f"https://github.com/{c["github"]["project"]}/"
            
            case URLType.Issue:
                issue_id = m.issues[self.extra] # type: ignore
                return f"https://github.com/{c["github"]["project"]}/issues/{issue_id}"
            
            case URLType.Comment:
                issue_id = m.issues[self.extra[0]] # type: ignore
                comment_id = m.comments[self.extra[1]] # type: ignore
                return f"https://github.com/{c["github"]["project"]}/issues/{issue_id}#issuecomment-{comment_id}"

def remap_attachments[T: Issue | Comment](c: dict, obj: T) -> T:
    p = re.compile(r"\[(.*?)\]\((\/uploads\/[0-9a-fA-F]+\/[^\/\s]+)\)")
    matches: list[tuple[re.Match, str]] = []

    sp: list[Process] = []

    body = obj.body

    for match in p.finditer(body):
        p = Process(target=download_file, args=(c, match.group(2)))
        p.start()
        sp.append(p)

        embed = ""

        if body[match.start(0)] == '!':
            embed = "!"

        matches.append((
            match,
            f"{embed}[{match.group(1)}](https://raw.githubusercontent.com/{c["github"]["project"]}/{c["github"]["branch"]}/.issue-porter/{c["gitlab"]["project"]}{match.group(2)})"
        ))

    for old, new in matches:
        print(f"{old.group()} => {new}")
        body = body.replace(old.group(), new, 1)

    obj.body = body

    # Wait until all subprocesses are finished
    for process in sp:
        process.join()

    return obj

def remap_urls[T: Issue | Comment](c: dict, obj: T, mapping: Mapping) -> T:
    p = re.compile("(https?://[^\\s]+)")
    matches: list[tuple[re.Match, str]] = []

    body = obj.body

    for match in p.finditer(body):
        matches.append((
            match,
            URL(match.group(), c)
                .remap(c, mapping)
        ))

    for old, new in matches:
        print(f"{old.group()} => {new}")
        body = body.replace(old.group(), new, 1)

    obj.body = body

    return obj

def remap_users[T: Issue | Comment](c: dict, obj: T, mapping: Mapping) -> T:
    p = re.compile(r"@[\w._]+") # @.+?(?= )
    matches: list[tuple[str, str]] = []

    body = obj.body

    for match in p.finditer(body):
        if match.group() in mapping.user:
            matches.append((match.group(), mapping.user[match.group()]))
        elif c["user-mapping"]["missing-user-behavior"] == "remove":
            matches.append((match.group(), c["user-mapping"]["missing-user-message"]))

    for old, new in matches:
        print(f"{old} => {new}")
        body = body.replace(old, new, 1)

    obj.body = body

    return obj

def remap[T: Issue | Comment](c: dict, obj: T, mapping: Mapping) -> T:
    return remap_attachments(c,
        remap_users(c,
            remap_urls(c, obj, mapping), mapping)
            )