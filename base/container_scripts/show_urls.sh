#!/bin/bash

# this gives us the show_urls django command
pip3 show django-extensions || pip3 install django-extensions

pulpcore-manager show_urls
