"""
Bluestock MF Capstone - Master Orchestrator
Runs the complete pipeline: generate datasets → ETL → analytics.
"""
import subprocess
import sys

steps = [
    ("Generating datasets", [sys.executable, "src/generate_datasets.py"]),
    ("Running ETL pipeline", [sys.executable, "src/etl_pipeline.py"]),
    ("Running analytics", [sys.executable, "src/analytics.py"]),
]

for name, cmd in steps:
    print(f"\n{'='*60}")
    print(f"Step: {name}")
    print(f"{'='*60}")
    result = subprocess.run(cmd, check=True)
    if result.returncode != 0:
        print(f"FAILED: {name}")
        sys.exit(1)

print("\n" + "="*60)
print("All steps completed successfully!")
print("Launch dashboard with: cd dashboard && streamlit run app.py")
print("="*60)
