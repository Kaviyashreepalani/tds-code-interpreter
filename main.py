from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from io import StringIO
import sys
import traceback
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CodeRequest(BaseModel):
    code: str

def execute_python_code(code: str):
    old_stdout = sys.stdout
    sys.stdout = StringIO()

    try:
        exec(code)
        output = sys.stdout.getvalue()
        return {
            "success": True,
            "output": output
        }

    except Exception:
        output = traceback.format_exc()
        return {
            "success": False,
            "output": output
        }

    finally:
        sys.stdout = old_stdout


@app.post("/code-interpreter")
def code_interpreter(req: CodeRequest):
    result = execute_python_code(req.code)

    if result["success"]:
        return {
            "error": [],
            "result": result["output"]
        }

    tb = result["output"]

    # Extract ONLY line numbers from the user's code
    error_lines = []

    for line in tb.splitlines():
        if 'File "<string>", line' in line:
            match = re.search(r'line (\d+)', line)
            if match:
                error_lines.append(int(match.group(1)))

    return {
        "error": error_lines,
        "result": tb
    }
