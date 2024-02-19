from pathlib import Path
import os
import subprocess
from pathlib import Path

home_wd = os.getcwd()

def viz_launch(viz_path):
    """Function to launch the visualisation """
    subprocess.run(f"streamlit run {str(viz_path)}", shell=True)
    return

if __name__ == "__main__":
    viz_launch(Path(home_wd, "pinkbombs", "viz", "main_viz.py"))

