# flask-code-nocodb
can't post data to table  Not Found The requested URL was not found on the server.

## Configuration

Set the NocoDB API key using the environment variable `NOCO_API_KEY` before
running the application:

```bash
export NOCO_API_KEY=your_token_here
```

The Flask app reads this variable to authenticate with the NocoDB API.

## Running the tests

Install the test requirements and execute the suite with `pytest`:

```bash
pip install flask requests pytest
pytest
```
