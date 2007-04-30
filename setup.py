#!/usr/bin/env python

from distutils.core import setup

setup(name="opengnss",
        version="0.1",
        author="Trond Danielsen",
        author_email="trond.danielsen@gmail.com",
        url="http://code.google.com/p/opengnss/",
        package_dir={'': 'src'},
        packages=['gps', 'gr-gnss'])





# vim: ai ts=4 sts=4 et sw=4

