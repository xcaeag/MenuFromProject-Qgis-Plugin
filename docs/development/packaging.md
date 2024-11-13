# Packaging and deployment

## Packaging

This plugin is using the [qgis-plugin-ci](https://github.com/opengisch/qgis-plugin-ci/) tool to perform packaging operations.  
Under the hood, the package command is performing a `git archive` run based on `CHANGELOG.md`.

Install additional dependencies:

```bash
python -m pip install -U -r requirements/packaging.txt
```

Then use it:

```bash
# package a specific version
qgis-plugin-ci package 1.3.1
# package latest version
qgis-plugin-ci package latest
```

## Release a version

Through git workflow:

1. Add the new version to the `CHANGELOG.md`. You can write it manually or use the auto-generated release notes by Github:
    1. Go to [project's releases](https://github.com/aeag/MenuFromProject-Qgis-Plugin/releases) and click on `Draft a new release`
    1. In `Choose a tag`, enter the new tag
    1. Click on `Generate release notes`
    1. Copy/paste the generated text from `## What's changed` until the line before `**Full changelog**:...` in the CHANGELOG.md replacing `What's changed` with the tag and the publication date
    1. Quit this tab without saving
1. Change the version number in `metadata.txt` with the next version and `DEV` suffix. Example : if you're about to release the version `2.2.0`, the next one will be `2.2.1-DEV`
1. Commit the changelog modification to main branch: `git commit -m "release: bump version to 2.2.0"`
1. Apply a git tag with the relevant version: `git tag -a 2.2.0 {git commit hash} -m "This version rocks!"`
1. Push tag to main branch: `git push origin 2.2.0`
