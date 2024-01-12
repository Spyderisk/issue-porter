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
from issue import Issue
from gitlab import issues as iter_issues, total_issues, get_repo_name
from github import first_pass, second_pass
import os

if os.name == 'nt':
    print (f"\nError: This program is not intended for use on Windows. This OS is {os.name}.\n")
    # exit(1)

conffile = "config.toml"
if os.path.isfile(conffile):
    c = tomllib.load(open(conffile, "rb"))
else:
    print (f"\nError: cannot file \"{conffile}\". Try copying from \"example_config.toml\".\n")
    exit(1)

c["repo_path"] = get_repo_name(c)

issues: list[Issue] = []
max_issues = total_issues(c)

for index, issue in enumerate(iter_issues(c)):
    print(f"Pulling issue {index + 1}/{max_issues}: {issue.title} ({issue.state})")
    issues.append(issue)
print("All issues parsed")

first_pass(c, issues)
second_pass(c, issues)


