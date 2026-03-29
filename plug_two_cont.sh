#!/bin/sh

printf "Available containers: \n"

docker compose ps
echo

printf "Please input container name: \n"

read CONT

echo
printf "Connecting to\n%s...\n\n" "$CONT"

docker exec -it $CONT bash

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    printf "\nDisconnected from $CONT... bye\n"
else
    printf "Connection to $CONT failed (exit code $EXIT_CODE). Available containers: \n\n""`docker compose ps`"

fi
