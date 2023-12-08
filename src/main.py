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

# Entry point

import tomllib
from gitlab import *

c = tomllib.load(open("config.toml", "rb"))

max_issues = total_issues(c)

for index, issue in enumerate(issues(c)):
    print(f"Pulling issue {index + 1}/{max_issues}: {issue.title} ({issue.state})")
print("All issues parsed")

max_comments = total_comments(c, 1312)

for index, comment in enumerate(issue_comments(c, 1312)):
    print(f"Pulling issue {index + 1}/{max_issues}")
