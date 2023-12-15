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

from issue import GithubID, GitlabID, GitlabIID

# Using a bidict so I can map back and forward
from bidict import bidict


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
    projects: DualDict[GitlabID, str, GithubID]
    issues: bidict[GitlabIID, GithubID]
    comments: bidict[GitlabID, GithubID]