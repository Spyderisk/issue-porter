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

# Github doesn't seem to be able to be self-hosted, so I'll hard code the API route
API_ROOT = "https://api.github.com"

def create_comment(c: dict, issue: Issue, com: Comment) -> GithubID:
    q = f"{API_ROOT}/repos/{c["github"]["project"]}/issues/{issue.meta.ids.github}/comments"
    data = {"body": com.body}

    r = post(q, data=json.dumps(data), headers={"Authorization": f"Bearer {c["github"]["access_token"]}"})
    sleep(0.5) # Rate limit
    return r.json()["id"]

def create_thread(c: dict, issue: Issue, thread: list[Comment]):
    for comment in thread:
        create_comment(c, issue, comment)

def create_issue(c: dict, issue: Issue) -> GithubID:
    data = {
        "title": issue.title,
        "body": issue.body
    }

    q = f"{API_ROOT}/repos/{c["github"]["project"]}/issues"
    r: Response = post(
        q,
        data=json.dumps(data),
        headers={"Authorization": f"Bearer {c["github"]["access_token"]}"}
    )

    sleep(0.5)

    return r.json()["number"]


def first_pass(c: dict, issues: list[Issue]) -> list[Issue]:
    for issue in issues:
        issue.meta.ids.github = create_issue(c, issue)

        for thread in issue.threads:
            create_thread(c, issue, thread)

    return issues

def second_pass(issues: list[Issue]):
    pass