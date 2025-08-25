import os
import subprocess
import sys
import tempfile

class PythonLocal:
    """
    Runs Python code locally instead of on E2B.
    """

    name = "python"
    system_message = """All Python code must include at least one print statement."""

    #     system_message = """
    #     # All Python code must include at least one print statement.
    #     # Your output dir is available os.environ['INTERPRETER_OUTPUT_DIR'].
    #     # A virtual environment is available at os.environ['INTERPRETER_VIRTUAL_ENV'] if you need to install packages.
    #     """

    def __init__(self):
        os.environ["INTERPRETER_OUTPUT_DIR"] = os.getenv("INTERPRETER_OUTPUT_DIR")
        os.environ["INTERPRETER_VIRTUAL_ENV"] = os.getenv("INTERPRETER_VIRTUAL_ENV")
        pass


    def run(self, code):
        """Generator that yields results in LMC format."""

        # Write code to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".py", mode="w") as f:
            f.write(code)
            tmp_path = f.name

        try:
            # Run the file in a subprocess
            proc = subprocess.Popen(
                [sys.executable, tmp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate()

            # Yield combined output in LMC format
            yield {
                "type": "console",
                "format": "output",
                "content": stdout + stderr
            }

        finally:
            pass  # you could delete tmp_path here if you want

    def stop(self):
        # For a real implementation, you could keep a reference
        # to the subprocess and kill it here.
        pass

    def terminate(self):
        # Cleanup resources if needed
        pass
