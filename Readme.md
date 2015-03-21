# Glob

A simple blog generator.

## Usage instructions

1. Create an empty directory tree for your content that looks like,

```bash
$ mkdir -p $DIR/{pages,posts,static}
```

2. Copy the `config.example.yml` into the directory as `config.yml`.

3. Copy the default css files into the `$DIR/static` directory.

3. Use the `blog.sh` script.

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

Simple `.md` or `.html` files whose content is just inserted into the base
template. The pages are generated on paths that match the directory structure
relative to the `pages/` directory.
