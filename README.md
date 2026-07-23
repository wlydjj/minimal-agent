# Minimal Agent

A minimal terminal agent built from scratch while following the
minimal-agent tutorial.

## What it does

-   Sends conversation history to an LLM
-   Parses one bash action from the model output
-   Executes the action in the local terminal
-   Returns command output to the model
-   Handles malformed model output
-   Handles command timeouts
-   Stops when the model requests exit

## Core loop

    User task
    → Query LLM
    → Parse action
    → Execute action
    → Return observation
    → Query LLM again

## Run

``` bash
cd ~/minimal-agent
source venv/bin/activate
python3 main.py
```

## Limitations

-   It executes model-generated shell commands on the local computer.
-   The model may not always follow the required output format.
-   The model API may be rate-limited.

This is a learning prototype, not a production-ready agent.
