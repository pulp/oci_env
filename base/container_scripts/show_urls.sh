#!/bin/bash

# this gives us the show_urls django command
uv pip show django-extensions || uv pip install django-extensions

pulpcore-manager show_urls
