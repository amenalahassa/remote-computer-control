import subprocess
import tempfile
import os

class PowerShellLocal:
    """
    Runs PowerShell code locally.
    """

    name = "powershell"
    # system_message = """
    # # All PowerShell code must include at least one Write-Output statement.
    # # Your output dir is available in $env:INTERPRETER_OUTPUT_DIR.
    # # A python virtual environment is available at $env:INTERPRETER_VIRTUAL_ENV if you need to install packages.
    # """
    system_message = """All PowerShell code must include at least one Write-Output statement."""


    def __init__(self):
        # Set environment variables to be used in the PowerShell script if needed
        os.environ["INTERPRETER_OUTPUT_DIR"] = os.getenv("INTERPRETER_OUTPUT_DIR")
        os.environ["INTERPRETER_VIRTUAL_ENV"] = os.getenv("INTERPRETER_VIRTUAL_ENV")
        pass

    def run(self, code):
        """Generator that yields results in LMC format."""

        # Write the PowerShell code to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ps1", mode="w", encoding="utf-8") as f:
            f.write(code)
            tmp_path = f.name

        try:
            # Run the PowerShell script
            # If you're on Windows with PowerShell 5.x, use "powershell"
            # If you have PowerShell Core (cross-platform), use "pwsh"
            proc = subprocess.Popen(
                ["powershell", "-ExecutionPolicy", "Bypass", "-File", tmp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            stdout, stderr = proc.communicate()

            yield {
                "type": "console",
                "format": "output",
                "content": stdout + stderr
            }

        finally:
            pass  # you can delete tmp_path here if you want

    def stop(self):
        # Could be implemented to terminate a running process
        pass

    def terminate(self):
        # Cleanup if needed
        pass
