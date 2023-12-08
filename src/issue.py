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

# Issue and comment data strucutures

# Type aliases for IDs
GitlabID = int
GithubID = int
IDs = tuple[GitlabID, GithubID | None]

class Meta:
    created_at: str
    updated_at: str | None

    def __init__(self, created_at: str, updated_at: str | None) -> None:
        self.created_at = created_at
        self.updated_at = updated_at

# While it'd make sense for this to be a tree structure,
# github operates in a linear way so it's easier to hold all comments together and sort by time
class Comment:
    id: IDs
    body: str
    attachments: list[str]
    parent: GitlabID | None # note id of parent comment
    meta: Meta

class Issue:
    id: IDs
    title: str
    body: str
    labels: list[str]
    state: str

    meta: Meta
    comments: list[Comment]
