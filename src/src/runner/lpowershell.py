import subprocess
import tempfile

class PowerShellLocal:
    """
    Runs PowerShell code locally.
    """

    name = "powershell"
    system_message = "# All PowerShell code must include at least one Write-Output statement."

    def __init__(self):
        # Needed so Open Interpreter can introspect __init__.__code__
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
