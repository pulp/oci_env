dynaconf list | grep -F "$1" | awk '{print $2}' | tr -d "'"
