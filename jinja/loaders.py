# -*- coding: utf-8 -*-
"""
    jinja.loaders
    ~~~~~~~~~~~~~

    Jinja loader classes.

    :copyright: 2006 by Armin Ronacher.
    :license: BSD, see LICENSE for more details.
"""

import codecs
from os import path
from jinja.parser import Parser
from jinja.translators.python import PythonTranslator
from jinja.exceptions import TemplateNotFound


def get_template_filename(searchpath, name):
    """
    Return the filesystem filename wanted.
    """
    return path.join(searchpath, path.sep.join([p for p in name.split('/')
                     if p and p[0] != '.']))


class LoaderWrapper(object):
    """
    Wraps a loader so that it's bound to an environment.
    """

    def __init__(self, environment, loader):
        self.environment = environment
        self.loader = loader

    def get_source(self, name, parent=None):
        """
        Retrieve the sourcecode of a template.
        """
        # just ascii chars are allowed as template names
        name = str(name)
        return self.loader.get_source(self.environment, name, parent)

    def parse(self, name, parent=None):
        """
        Retreive a template and parse it.
        """
        # just ascii chars are allowed as template names
        name = str(name)
        return self.loader.parse(self.environment, name, parent)

    def load(self, name, translator=PythonTranslator):
        """
        Translate a template and return it. This must not necesarily
        be a template class. The javascript translator for example
        will just output a string with the translated code.
        """
        # just ascii chars are allowed as template names
        name = str(name)
        return self.loader.load(self.environment, name, translator)


class FileSystemLoader(object):
    """
    Loads templates from the filesystem::

        from jinja import Environment, FileSystemLoader
        e = Environment(loader=FileSystemLoader('templates/'))
    """

    def __init__(self, searchpath, use_cache=False, cache_size=40):
        self.searchpath = searchpath
        self.use_cache = use_cache
        self.cache_size = cache_size
        self.cache = {}

    def get_source(self, environment, name, parent):
        filename = get_template_filename(self.searchpath, name)
        if path.exists(filename):
            f = codecs.open(filename, 'r', environment.template_charset)
            try:
                return f.read()
            finally:
                f.close()
        else:
            raise TemplateNotFound(name)

    def parse(self, environment, name, parent):
        source = self.get_source(environment, name, parent)
        return Parser(environment, source, name).parse()

    def load(self, environment, name, translator):
        if self.use_cache:
            key = (name, translator)
            if key in self.cache:
                return self.cache[key]
            if len(self.cache) >= self.cache_size:
                self.cache.clear()
        rv = translator.process(environment, self.parse(environment, name, None))
        if self.use_cache:
            self.cache[key] = rv
        return rv