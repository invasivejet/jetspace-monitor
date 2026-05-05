import os

import modal

app = modal.App("jetspace-secret-probe")


@app.function(secrets=[modal.Secret.from_name("custom-secret")])
def show_secret_key_presence() -> dict:
    # Only return metadata, never print the secret value.
    val = os.environ.get("jetspace", "")
    return {
        "has_jetspace_secret": bool(val),
        "secret_length": len(val),
    }


@app.local_entrypoint()
def main() -> None:
    print(show_secret_key_presence.remote())
