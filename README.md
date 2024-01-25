# Issue-Porter

Minimum Python Version: 3.12.1
Gitlab API version: v4
Github API version: 2022-11-28


**THIS TOOL IS STILL IN EARLY DEVELOPMENT AND NOT ALL FEATURES ARE FINISHED, USE AT YOUR OWN RISK**  
To do list:

- ~~Parse GitLab issues + comments~~
- ~~Strip out closed issues if required~~
- Push all data to GitHub including the GitLab-specific metadata with ~~relationships between issues and comments~~ (TODO: fully test mapping)
- implement attachment handling (GitHub has no API for Issue attachments). Push images to .github-issue-images-from-gitlab or similar, and link from the Issue
- ~~Implement link mapping (map from GitLab links to GitHub ones)~~
- ~~Implement user mapping (map from GitLab users to GitHub ones)~~
- Implement file url mapping
- Implement system to apply the above mappings in an editing pass of all the new GitHub issues

## About

This is a tool to port issues from GitLab to GitHub.

More of the technical documentation is in the configuration file, see
`example_config.toml` for details.

## Brief overview

The data models differ in important ways, e.g. GitLab has threaded comments but
GitHub does not. Another difficulty is that GitHub does not expose an API to
upload attachments such as screenshots. The GitHub API does not allow us to
specify what the new GitHub Issue number will be. Many of these problems and more
have been solved using the GitHub feature that Issues have versions. This allows us
to do multiple passes, editing the newly-created GitHub issues to add in
relationships between Issues and their dependent comments, and file attachments
we have uploaded via Git, and of course the maps between GitLab issue numbers
and GitHub issue numbers.

## Setup
```
git clone https://github.com/Spyderisk/issue-porter.git
cd issue-porter
```

#### Setup a virtual environment (optional but recommended)
```
python3.12 -m venv .venv
source .venv/bin/activate
```
#### Install dependencies
```
python3.12 -m pip install -r requirements.txt
```

## Usage
```
cp example_config.toml config.toml
```
Edit config.toml with your favourite text editor / IDE / magnet + needle.

This contains all the configuration the program requires
```
python3.12 src/main.py
```
