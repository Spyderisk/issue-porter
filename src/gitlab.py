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

# Gitlab Wrangler
# Here we parse issues and comments

from requests import get, Response
from issue import Issue, Comment, Meta, ID, GitlabID, GitlabIID, CommentType
from typing import Generator, Any, Callable
from math import ceil

PER_PAGE = 20


def __paginate[T](c: dict, total: int, refill_bag: Callable[[dict, int], list[T]]) -> Generator[T, Any, None]:
    """Helper for creating a generator over gitlabs pages."""
    print(total)
    index = 0
    bag: list[T] = []

    while index < total:
        if len(bag) == 0:
            bag = refill_bag(c, ceil(index / PER_PAGE) + 1)
            if len(bag) == 0:
                break
        yield bag.pop()
        index += 1


def gl_get(req: str, ext: str, c: dict) -> Response:
    q = f"https://{c['gitlab']['domain']}/api/v4/{req}?access_token={c['gitlab']['access_token']}&{ext}"
    # print(q)
    r = get(q)
    return r


def get_issues(c: dict, transfer_label: str | None, page: int = 1, per_page: int = PER_PAGE) -> Response:
    if transfer_label:
        return gl_get(f"projects/{c['gitlab']['project']}/issues",
                      f"labels={transfer_label}&per_page={per_page}&page={page}", c)
    else:
        return gl_get(f"projects/{c['gitlab']['project']}/issues",
                      f"per_page={per_page}&page={page}", c)


def get_discussion(c: dict, issue_id: GitlabID, page: int = 1, per_page: int = PER_PAGE) -> Response:
    return gl_get(f"projects/{c['gitlab']['project']}/issues/{issue_id}/discussions",
                  f"per_page={per_page}&page={page}", c)


def __parse_issue(r) -> Issue:
    issue = Issue()

    issue.title = r["title"]
    issue.body = r["description"]
    issue.labels = r["labels"]
    issue.state = r["state"]
    issue.meta = Meta(
        r["created_at"],
        r["updated_at"],
        ID(r["id"], r["iid"])
    )

    return issue


def __parse_issue_page(c: dict, r: Response) -> list[Issue]:
    bag = []

    body = r.json()

    for issue in body:
        bag.append(__parse_issue(issue))

    return bag


def total_issues(c: dict) -> int:
    return int(
        get_issues(c, c["gitlab"]["transfer_label"], 0, 1)
        .headers["x-total"]
    )


# Iterator over gitlab issues
def issues(c: dict) -> Generator[Issue, Any, None] | list:
    total = total_issues(c)

    if total == 0:
        print("No issues to migrate!")
        return []

    def get_bag(c: dict, page: int) -> list[Issue]:
        print(f"\nFetching gitlab bag {page}")
        issues = get_issues(c, c["gitlab"]["transfer_label"], page)

        print(f"Parsing gitlab bag {page}")
        issues = __parse_issue_page(c, issues)

        for issue in issues:
            threads = list(issue_comments(
                c, issue.meta.ids.gitlab_internal))  # type: ignore

            issue.threads = threads

        return issues

    return __paginate(
        c,
        total,
        get_bag
    )


def __parse_comment(r, parent: GitlabID | None) -> Comment:
    comment = Comment()

    comment.comment_type = CommentType.System if r["system"] else CommentType.User
    comment.body = r["body"]
    comment.attachments = r["attachment"]
    comment.parent = parent
    comment.meta = Meta(
        r["created_at"],
        r["updated_at"],
        ID(r["id"], None)
    )

    return comment


def __parse_thread(r) -> list[Comment]:
    thread = []
    last_id = None
    for note in r["notes"]:
        comment = __parse_comment(note, last_id)
        last_id = comment.meta.ids.gitlab
        thread.append(comment)
    return thread


def __parse_discussion_page(r: Response) -> list[list[Comment]]:
    threads = []

    for thread in r.json():
        thread = __parse_thread(thread)
        threads.append(thread)

    return threads


def total_threads(c: dict, issue_id: GitlabID) -> int:
    return int(
        get_discussion(c, issue_id, 1, 1)
        .headers["x-total"]
    )


def issue_comments(c: dict, id: GitlabIID) -> Generator[list[Comment], Any, None] | list:
    total = total_threads(c, id)

    if total == 0:
        print("No issues to migrate!")
        return []

    def get_bag(c, page: int) -> list[list[Comment]]:
        print(f"\nFetching gitlab bag {page}")
        comments = get_discussion(c, id, page)

        print(f"Parsing gitlab bag {page}")
        return __parse_discussion_page(comments)

    return __paginate(
        c,
        total,
        get_bag
    )
