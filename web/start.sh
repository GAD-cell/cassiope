#!/bin/bash

(
    set -Ee

    function _catch {
        echo "Error: $1"
        exit 0  # optional; use if you don't want to propagate (rethrow) error to outer shell
    }
    function _finally {
        echo -e "\n\nCleaning up..."
    }

    trap _catch ERR
    trap _finally EXIT
    (trap 'kill 0' SIGINT;
        cd backend && flask run --port=5001 &
        cd frontend && npm start
    )
)
