#!/bin/bash

# this gives us the show_urls django command
python3 -m pip show django-extensions || python3 -m pip install django-extensions

pulpcore-manager show_urls
