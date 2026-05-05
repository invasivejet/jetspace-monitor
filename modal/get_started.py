import modal

app = modal.App("jetspace-get-started")


@app.function()
def square(x: int) -> int:
    print("Remote worker executing square()")
    return x * x


@app.local_entrypoint()
def main() -> None:
    print("the square is", square.remote(42))
