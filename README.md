# Issue-Porter

Minimum Python Version: 3.12.1
Gitlab API version: v4
Github API version: 2022-11-28

## About

This is a tool to port issues from GitLab to GitHub. There are several such
tools around, but as of March 2024 this appears to be the most complete and
effective. There are outstanding items to fix (see TODO section below) but this
is a very good start.

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

## What needs to be completed

- Push all data to GitHub including the GitLab-specific metadata with (TODO: fully test mapping)
- Implement file url mapping
- Implement system to apply the above mappings in an editing pass of all the new GitHub issues

## Setup

```bash
git clone https://github.com/Spyderisk/issue-porter.git
cd issue-porter
```

### Setup a virtual environment (optional but recommended)

```bash
python3.12 -m venv .venv
source .venv/bin/activate
```

### Install dependencies

```bash
python3.12 -m pip install -r requirements.txt
```

## Usage

```bash
cp example_config.toml config.toml
```

Edit config.toml with your favourite text editor / IDE / magnet + needle.

To generate the persistent config, run:

```bash
python3.12 src/main.py --gen-mapping
```

This will clone `github.storage_repo` and place it into `storage_repo/` where you can edit `storage_repo/.issue-porter/user_mapping.toml`

To finally port the issues, run:

```bash
python3.12 src/main.py
```
