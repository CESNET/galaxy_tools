# CESNET Galaxies Tool Management

## to install a repo

Create an entry in `GALAXY_URL/section_ID.yml` and open a PR.

For `galaxy-umsa.grid.cesnet.cz/matchms.yml` it'd look like this:

```
tool_panel_section_label: matchms
tools:
- name: matchms_subsetting
  owner: recetox
- name: matchms_metadata_merge
  owner: recetox
```
