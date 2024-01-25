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

# Github wrangler
# Here we create issues and comments

from issue import Issue, Comment, GithubID
from requests import post, Response
import json
from time import sleep
from mapping import Mapping, remap
from git_storage import PersistentStorage as PS

# Github doesn't seem to be able to be self-hosted, so I'll hard code the API route
API_ROOT = "https://api.github.com"


def create_comment(c: dict, issue: Issue, com: Comment) -> GithubID:
    q = f"{API_ROOT}/repos/{c["github"]["project"]}/issues/{issue.meta.ids.github}/comments"
    data = {"body": com.body}

    r = post(q, data=json.dumps(data), headers={"Authorization": f"Bearer {c["github"]["access_token"]}", "X-GitHub-Api-Version": "2022-11-28"})
    sleep(0.5)  # Rate limit
    return r.json()["id"]


def create_issue(c: dict, issue: Issue) -> GithubID:
    labels = []
    if c["github"]["ported_issue_label"]:
        labels = [c["github"]["ported_issue_label"]]

    data = {
        "title": issue.title,
        "body": issue.body,
        "labels": labels
    }

    q = f"{API_ROOT}/repos/{c["github"]["project"]}/issues"
    r: Response = post(
        q,
        data=json.dumps(data),
        headers={
            "Authorization": f"Bearer {c["github"]["access_token"]}",
            "X-GitHub-Api-Version": "2022-11-28"
        }
    )

    sleep(0.5)  # Rate limit

    return r.json()["number"]


def edit_comment(c: dict, issue: Issue, com: Comment):
    q = f"{API_ROOT}/repos/{c["github"]["project"]}/issues/comments/{com.meta.ids.github}"
    data = {"body": com.body}

    r = post(q, data=json.dumps(data), headers={"Authorization": f"Bearer {c["github"]["access_token"]}", "X-GitHub-Api-Version": "2022-11-28"})
    sleep(0.5)  # Rate limit


def edit_issue(c: dict, issue: Issue):
    labels = []
    if c["github"]["ported_issue_label"]:
        labels = [c["github"]["ported_issue_label"]]

    data = {
        "title": issue.title,
        "body": issue.body,
        "labels": labels
    }

    q = f"{API_ROOT}/repos/{c["github"]["project"]}/issues/{issue.meta.ids.github}"
    r: Response = post(
        q,
        data=json.dumps(data),
        headers={"Authorization": f"Bearer {c["github"]["access_token"]}"}
    )

    sleep(0.5)  # Rate limit


def first_pass(c: dict, issues: list[Issue]) -> list[Issue]:
    for issue in issues:
        issue.meta.ids.github = create_issue(c, issue)

        for thread in issue.threads:
            for comment in thread:
                comment.meta.ids.github = create_comment(c, issue, comment)

    return issues


def second_pass(c: dict, issues: list[Issue], ps: PS):
    mapping = Mapping(c["gitlab"]["repo_path"], c["github"]["project"])
    mapping.collect_ids(issues)
    mapping.init_persistent_mapping(c, ps)

    for issue in issues:
        issue: Issue = remap(c, issue, mapping)
        edit_issue(c, issue)

        for thread in issue.threads:
            for comment in thread:
                comment: Comment = remap(c, comment, mapping)
                edit_comment(c, issue, comment)
