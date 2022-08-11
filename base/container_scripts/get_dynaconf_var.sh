dynaconf list | fgrep $1 | awk '{print $2}' | tr -d "'"
