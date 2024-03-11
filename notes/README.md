# Issue Porter Notes

## How it works

### Gitlab source project

We use the [API](https://docs.gitlab.com/ee/api/rest/) to download the Issue comments. Unfortunately there's no API to download attachments, for example screenshots. For this, at the moment for test and demonstration, we use a browser session token taken from the Inspector (F12 in Firefox/Chrome) which we use in a 'curl' commandline to download the files directly off the server. 

### GitHub destination project

This end is a little more complex. To retain as much information as possible, we first push the unedited comments along with a metadata addendum describing XXXXX (UNIMPLEMENTED YET). We then do a second pass once we have information from processing all of the GitLab issues, and edit the GitHub issues to replace GitLab usernames with their GitHub equivalents, and upload attachments, etc.

### Mappings

Mapping for users and files between GitLab and GitHub are all inside the storage repo. Some are generated and remain persistent across Issue Porter runs so links may be updated. Some are written by the user.  

#### Link Mapping

It may be desired to be able to continuously port over issues, so development may run in parallel across platforms, therefore we have the ability to store information about the repo, such as issue IDs so they may be mapped for links in new issues. 

#### User Mapping

The user must write the mapfile manually. We store the configs for this inside `storage_repo/.issue-porter/user_mapping.toml` The program will generate an example mapfile if you run it with `--gen-mapping`.

When issues are brought across from GitLab, the mapping will connect eg user sally93821 with SallyJones, and on GitHub SallyJones will be notified that she has been mentioned in these issues as if they were new issues (which of course they are, from GitHub's point of view.) This can potentially invoke a blizzard of notifications if there are thousands of issues XXXXX.

#### Attachment mapping

Attachments in GitLab look like this:

```
![test](/uploads/bbd250669db0b181297906d9a25c7b05/test.png)
```

To download this we use a browser session token, and use the full url `https://{HOST}/{USER}/{REPO}/{RELATIVE URL}`. An example full `curl` invocation is:

```
XXXX
```

The file downloaded by `curl` gets placed inside `storage_repo/.issue-porter/{REPO_ID}/{RELATIVE URL}` which can then be committed to GitHub. An entry is added to the issue with a link to this file.
