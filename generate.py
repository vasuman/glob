#!/usr/bin/env python2

import yaml
from datetime import date
from StringIO import StringIO
from jinja2 import Environment, FileSystemLoader
import argparse
import sys
import os
from posixpath import join
from os.path import splitext, exists, basename, dirname, realpath, relpath
from markdown import Markdown, markdownFromFile
from shutil import copytree, rmtree
import time
from collections import namedtuple
import random

MKD_EXT = ['extra', 'meta', 'codehilite(linenums=True)', 'def_list']

TIME_FORMAT_READ = '%d-%m-%Y'
TIME_FORMAT_WRITE = '%d %b %Y'
TIME_FORMAT_RFC = '%Y-%m-%d'

CONFIG_FILE = 'config.yml'
TEMPLATES_DIR = 'templates'
POSTS_DIR = 'posts'
PAGES_DIR = 'pages'
STATIC_DIR = 'static'

POST_PREFIX = 'posts'

flags = None

FLAG_SKIP_DRAFTS = '-skipdrafts'

def group_posts(posts):
    PostGroup = namedtuple('PostGroup', ['month', 'year', 'posts'])
    def eq(p, x):
        return x.month == p.ts.tm_mon and x.year == p.ts.tm_year
    cls = []
    def add_to_class(post):
        for cl in cls:
            if eq(post, cl):
                cl.posts.append(post)
                return True
            return False
    for post in posts:
        if not add_to_class(post):
            cls.append(PostGroup(post.ts.tm_mon, post.ts.tm_year, [post]))
    return sorted(cls, key = lambda x: x.year * 12 + x.month, reverse = True)

def date_ordinal(day):
    if 4 <= day <= 20 or 24 <= day <= 30:
        suffix = "th"
    else:
        suffix = ["st", "nd", "rd"][day % 10 - 1]
    return str(day) + suffix

def ignore_file(fname):
    return fname.endswith('.swp') or fname.startswith('.') or fname.startswith('#')

def each_file(dir_path, func):
    for fdir, _, fnames in os.walk(dir_path):
        for fname in fnames:
            if ignore_file(fname):
                print 'Ignoring, ', fname
                continue
            path = join(fdir, fname)
            print path
            func(path)

def parse_date(date_str):
    return time.strptime(date_str, TIME_FORMAT_READ)

def select_random(xs):
    return random.choice(xs)

def group_qual(g):
    return date(g.year, g.month, 1).strftime('%B %Y')

def readable_time(t):
    return time.strftime(TIME_FORMAT_WRITE, t)

def format_time(t):
    return time.strftime(TIME_FORMAT_RFC, t)

def add_helpers(env):
    env.globals.update(select_random = select_random)
    env.globals.update(readable_time = readable_time)
    env.globals.update(format_time = format_time)
    env.globals.update(group_qual = group_qual)
    env.globals.update(date_ordinal = date_ordinal)

def get_html(md_path):
    s = StringIO()
    markdownFromFile(md_path, s, extensions = MKD_EXT)
    return s.getvalue()

class Post:
    def __init__(self, post_path):
        self.path = post_path
        md = Markdown(extensions = MKD_EXT, output_format = 'xhtml5')
        buf = StringIO()
        md.convertFile(input = self.path, output = buf)
        self.html = buf.getvalue()
        buf.close()
        if 'slug' in md.Meta:
            self.slug = md.Meta['slug'][0]
        else:
            self.slug, _ = splitext(basename(post_path))
        print self.slug
        self.title = md.Meta['title'][0]
        self.ts = parse_date(md.Meta['date'][0])
        self.draft = 'draft' in md.Meta
        self.out_path = self._get_path()
        self.flags = md.Meta['flags'] if 'flags' in md.Meta else []

    def _get_path(self):
        date_path = '{}/{}/{}'.format(self.ts.tm_year, self.ts.tm_mon, self.ts.tm_mday)
        return join(POST_PREFIX, date_path, self.slug) + '.html'

    def render(self, tmpl, ctx):
        f_path = join(ctx.out_dir, self.out_path)
        f_dir = dirname(f_path)
        if not exists(f_dir):
            os.makedirs(f_dir)
        with open(f_path, 'wb') as f:
            out = tmpl.render(post = self, config = ctx.config)
            f.write(out.encode('utf-8'))

class StaticGenerator:
    def __init__(self, src_dir, out_dir):
        self.src_dir = src_dir
        self.out_dir = out_dir
        cfg_path = join(self.src_dir, CONFIG_FILE)
        self.config = yaml.load(open(cfg_path))
        template_path = join(get_self_path(), TEMPLATES_DIR)
        self.env = Environment(loader = FileSystemLoader(template_path))
        add_helpers(self.env)
        self._posts = []

    def generate(self):

        # For each page!
        def process_page(page_path):
            print 'Processing page, ', page_path
            name, ext = splitext(page_path)
            page_name = relpath(name, pages_path) + '.html'
            if ext == '.md':
                html = get_html(page_path)
            elif ext == '.html':
                html = open(page_path, 'rb').read()
            else:
                print 'File extension {} not supported'.format(ext)
                return
            html = html.decode('utf-8')
            out_path = join(self.out_dir, page_name)
            out_dir = dirname(out_path)
            if not exists(out_dir):
                os.makedirs(out_dir)
            with open(out_path, 'wb') as f:
                page_html = base.render(content = html, config = self.config)
                f.write(page_html.encode('utf-8'))

        # For each post
        def process_post(post_path):
            print 'Processing post, ', post_path
            post = Post(post_path)
            if (FLAG_SKIP_DRAFTS in flags) and post.draft:
                return
            self._posts.append(post)
            post_template = self.env.get_template('post.html')
            post.render(post_template, self)

        # Generate posts
        posts_path = join(self.src_dir, POSTS_DIR)
        blog_dir = join(self.out_dir, POST_PREFIX)
        if os.path.exists(blog_dir):
            rmtree(blog_dir)
        each_file(posts_path, process_post)

        # Generate pages
        base = self.env.get_template('base.html')
        pages_path = join(self.src_dir, PAGES_DIR)
        each_file(pages_path, process_page)

        # Generate index page
        archives = self.env.get_template('index.html')
        with open(join(self.out_dir, 'index.html'), 'wb') as f:
            groups = group_posts(self._posts)
            f.write(archives.render(config = self.config, groups = groups))

        # Copy static files
        out_static = join(self.out_dir, STATIC_DIR)
        if exists(out_static):
            rmtree(out_static)
        copytree(join(self.src_dir, STATIC_DIR), out_static)

def get_self_path():
    return dirname(realpath(__file__))

def main():
    global flags
    src_dir = sys.argv[1]
    out_dir = sys.argv[2]
    if not exists(out_dir):
        os.makedirs(out_dir)
    flags = sys.argv[3:]
    gen = StaticGenerator(src_dir, out_dir)
    gen.generate()

if __name__ == '__main__':
    main()
