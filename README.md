# Issue-Porter

Minimum Python Version: 3.12.1
Gitlab API version: v4
Github API version: 2022-11-28

## About

This is a tool to port issues from GitLab to GitHub. There are several such
tools around, but as of March 2024 this appears to be the most complete and
effective. There are outstanding items to fix (see TODO section below) but this
is a very good start. We would love to have your corrections and improvements.

More of the technical documentation is in the configuration file, see
`example_config.toml` for details.

## Brief overview

The data models differ in important ways, including:

* GitLab has threaded comments but GitHub does not. 
* Gitlab does not have a an API to download attachments such as screenshots, and GitHub does not expose an API to upload attachments.
* The GitHub API does not allow us to specify what the new GitHub Issue number will be.
* Internal links across the two platforms will be different, for example links to other issues.

Many of these problems and more have been solved using the GitHub feature that
Issues have versions. This allows us to do multiple passes, editing the
newly-created GitHub issues to add in relationships between Issues and their
dependent comments, and file attachments we have uploaded via Git, and of
course the maps between GitLab issue numbers and GitHub issue numbers.

## TODO

- Push all data to GitHub including the GitLab-specific metadata
- Implement file url mapping. This means if I link to a README.md file in a certain branch, we remap this link to work in the other platform
- Fully test the tool/create test repos
- Implement a system to run a second pass of porting issues. This could be desireable if development happens on Gitlab, but you want to publish to Github. What we want is to be able to save our mapping (Issue IDs, usernames etc) and to be able to use this information later to fully remap this second pass, along with potentially extending the original remap with new information

## Demo

Once you have completed the Setup section below, the minimum demonstration of Issue Porter is:

Given a Gitlab repo and a Github repo,
Find the ID of the gitlab repo (Located next to it's name on the repo's root page) and the user/repo_name for github.
Copy these into the config.toml, also changing other values if it is appropriate to your case.
Run `python3.12 src/main.py port` in your terminal.


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
python3.12 src/main.py init
```

This will clone `github.storage_repo` from the config and place it into `storage_repo/` where you can edit `storage_repo/.issue-porter/user_mapping.toml`

To finally port the issues, run:

```bash
python3.12 src/main.py port
```
