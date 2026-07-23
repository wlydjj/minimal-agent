import re
import subprocess
import os
from zhipuai import ZhipuAI

client = ZhipuAI(
    api_key="5405c08898ae433893134a1db7f6f3da.feik4QRGco7UQkBs"
)

env_vars = {
    "PAGER": "cat",
    "MANPAGER": "cat",
    "LESS": "-R",
    "PIP_PROGRESS_BAR": "off",
    "TQDM_DISABLE": "1",
}

incorrect_format_message = """Your output was malformatted.
Please include exactly 1 action formatted as in the following example:

```bash-action
ls -R
```
"""

class NonTerminatingException(RuntimeError):
    """The agent can recover and continue."""
class OurTimeoutError(NonTerminatingException):
    """The command timed out, but the LM may try another action."""
class FormatError(NonTerminatingException):
    """The LM output format was invalid, so it should try again."""
class TerminatingException(RuntimeError):
    """The agent should stop."""
class Submitted: ...  # agent wants to stop

def query_lm(messages):
    response = client.chat.completions.create(
        model="glm-4.7-flash",
        messages=messages
    )
    return response.choices[0].message.content

def parse_action(lm_output: str) -> str:
    """Take LM output, return action"""
    matches = re.findall(
        r"```bash-action\s*\n(.*?)\n```", 
        lm_output, 
        re.DOTALL
    )
    if not len(matches) == 1:
       raise FormatError(incorrect_format_message)
    return matches[0].strip()

def execute_action(action: str) -> str:
    """Execute action, return output"""
    if action == "exit":
        raise TerminatingException("LM requested to quit")
    try:
        result = subprocess.run(
            action,
            shell=True,
            text=True,
            env=os.environ | env_vars,
            encoding="utf-8",
            errors="replace",
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            timeout=30,
        )
        return result.stdout
    except TimeoutError as e:
        raise OurTimeoutError("Your last command time out, you might want to ...") from e

# Main agent loop
messages = [{
    "role": "system", 
    "content": """
You are a helpful assistant.
When you want to run a command, wrap it exactly like this:

```bash-action
ls
```

To finish, output:
exit
"""
}, {
    "role": "user", 
    "content": "List the files in the current directory"
}]

while True:
    try:
        lm_output = query_lm(messages)
        print("LM output", lm_output)
        messages.append({"role": "assistant", "content": lm_output})  # remember what the LM said
        action = parse_action(lm_output)  # separate the action from output
        print("Action", action)
        output = execute_action(action)
        print("Output", output)
        messages.append({"role": "user", "content": output})  # send command output back
    except NonTerminatingException as e:
        messages.append({"role": "user", "content": str(e)})
    except TerminatingException as e:
        print("Stopping because of ", str(e))
        break
