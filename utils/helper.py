import subprocess
import time
import logging

logging.basicConfig(level=logging.DEBUG)

def run_ollama(model:str, system_prompt:str, user_prompt:str, max_tries=10, timeout=300) -> str:
    if system_prompt:
        prompt = f"<|system|>\n{system_prompt}\n<|end|>\n<|user|>\n{user_prompt}\n<|end|>\n"
    else:
        prompt = f"<|user|>\n{user_prompt}\n<|end|>\n"
    response = None
    while response is None and max_tries > 0:
        max_tries -= 1
        try:
            result = subprocess.run(
                ["ollama", "run", model],
                input=f"{prompt}".encode("utf-8"),
                capture_output=True,
                check=True,
                timeout=timeout
            )
            response = result.stdout.decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            logging.warning(f"Ollama Error: {e}. Re-run in 5 seconds... Attempts left: {max_tries}")
            time.sleep(5)
        except KeyboardInterrupt:
            logging.warning("User KeyboardInterrupt.")
            raise
        except Exception as e:
            logging.error(f"Error: {e}. Re-run in 5 seconds... Attempts left: {max_tries}")
            time.sleep(5)

    if response is None:
        raise RuntimeError("Failed to get response from Ollama after max_tries.")
    
    logging.debug(f"Model: {model}\n""Prompt:\n {user_prompt}\n""Result: {response}\n")
    return response
