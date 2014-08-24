# Glob

A simple blog generator.

## Usage instructions

1. Use the `config.yml.template` file to generate a `config.yml`

2. Create or link to a `posts` and a `pages` directory

### Posts

Must follow the template

```yaml
title: Post Title
slug: slug-of-post
date: 01-01-1993

Enter post content after leaving a blank line.
This is *markdown* formatted content
```

### Pages

Simple `.md` or `.html` files whose content is just inserted into the base template. The pages are generated on paths that match the directory structure relative to the `pages/` directory.
