#!/bin/bash

# this gives us the show_urls django command
pip show django-extensions || pip install django-extensions

pulpcore-manager show_urls
