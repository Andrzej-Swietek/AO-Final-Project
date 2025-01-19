#!/bin/bash

# Start Flask app in the background
flask run --host=0.0.0.0 &

# Start RQ worker in the background
rq worker &

# Wait indefinitely so the container doesn't exit
wait