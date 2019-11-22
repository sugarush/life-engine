#!/usr/bin/env zsh
local pids=( )

if [ -z $(command -v mongod) ]; then
  echo "Missing mongod."
  return 1
fi

if [ -z $(command -v livereload) ]; then
  echo "Missing livereload."
  return 1
fi

if [ -z $(command -v python) ]; then
  echo "Missing python."
  return 1
fi

MONGODB_DATA="mongodb_data"

if [ ! -d "${MONGODB_DATA}" ]; then
  mkdir -p "${MONGODB_DATA}"
fi

mongod --dbpath "${MONGODB_DATA}" &
pids+=("$!")

python test_server &
pids+=("$!")

python -m http.server 8000 &
pids+=("$!")

livereload &
pids+=("$!")

trap "kill_pids" SIGINT

function kill_pids() {
  for pid in ${pids[@]}; do
    kill -TERM "${pid}"
  done
}

for pid in ${pids[@]}; do
  wait "${pid}"
done
