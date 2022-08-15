dynaconf list | fgrep $1 | awk '{print $2}' | tr -d "'" > /src/$COMPOSE_PROJECT_NAME/.compiled/dynaconf_stdout
cat /src/$COMPOSE_PROJECT_NAME/.compiled/dynaconf_stdout