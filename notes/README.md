# Issue Porter Notes

## How it works

### Gitlab

We use the [API](https://docs.gitlab.com/ee/api/rest/) to grab the comments. Unfortunately there's no api to download attachments. For this we use a browser session token which can be used to curl the files directly off the server.

### Github

This end is a little more complex. To retain as much information as possible, we first push the unedited comments along with a metadata addendum (UNIMPLEMENTED YET). After this we can edit the comments to replace old user mentions and attachments etc.

### Mappings

These are all stored inside the storage repo. Some are generated and remain persistent across runs so links may be updated, and some are written by the user.

#### Link Mapping

It may be desired to be able to continuously port over issues, so development may run in parallel across platforms, therefore we have the ability to store information about the repo, such as issue IDs so they may be mapped for links in new issues. 

#### User Mapping

It makes sense to let the user write this manually. We store the configs for this inside `storage_repo/.issue-porter/user_mapping.toml` The program will generate an example one if you run it with `--gen-mapping`

#### Attachment mapping

Attachments in gitlab look as such:

```
![test](/uploads/bbd250669db0b181297906d9a25c7b05/test.png)
```

To download this we use a browser session token, and use the full url `https://{HOST}/{USER}/{REPO}/{RELATIVE URL}`

This gets placed inside `storage_repo/.issue-porter/{REPO_ID}/{RELATIVE URL}` which can then be commited to Github and linked.