"""
CI Lint Check — Syntax validation, import check, and Streamlit entry point verification.
Run locally:  python ci/lint_check.py
Run in CI:    python ci/lint_check.py
"""

import ast
import importlib
import os
import sys


# Environment-agnostic markers (avoid emoji encoding issues on Windows)
CHECK = "[check]"
PASS = "[PASS]"
FAIL = "[FAIL]"
SKIP = "[SKIP]"


def check_syntax():
    """Check all .py files for syntax errors."""
    print(f"{CHECK} Checking Python syntax...")
    errors = 0
    for root, dirs, files in os.walk("."):
        dirs[:] = [
            d
            for d in dirs
            if d not in (".git", "__pycache__", ".venv", "node_modules", ".github")
        ]
        for f in files:
            if not f.endswith(".py"):
                continue
            path = os.path.join(root, f)
            try:
                with open(path, encoding="utf-8") as fh:
                    ast.parse(fh.read())
            except SyntaxError as e:
                print(f"  {FAIL} {path} -- {e}")
                errors += 1
    if errors:
        print(f"  {FAIL} {errors} file(s) with syntax errors")
        sys.exit(1)
    print(f"  {PASS} All Python files passed syntax check.")


def validate_imports():
    """Import each util module and verify expected names exist."""
    print(f"\n{CHECK} Validating imports...")

    # Expected names per module (from app.py usage)
    expected_names = {
        "utils.data_loader": ["load_data", "get_data_info"],
        "utils.preprocessing": ["clean_data", "create_customer_summary"],
        "utils.segmentation": [
            "calculate_rfm_scores",
            "label_segments_rfm",
            "get_segment_summary",
            "perform_kmeans_clustering",
            "find_optimal_k",
        ],
        "utils.predictive": [
            "compute_clv",
            "compute_churn_probability",
            "compute_mom_metrics",
            "engineer_features",
        ],
        "utils.ui_components": ["hero_header", "section_header"],
    }

    # report_generator only if reportlab is available
    try:
        import reportlab  # noqa: F401
        expected_names["utils.report_generator"] = ["generate_report"]
    except ImportError:
        print(f"  {SKIP} reportlab not installed -- skipping report_generator")

    errors = 0
    for mod_name, names in expected_names.items():
        try:
            mod = importlib.import_module(mod_name)
        except Exception as e:
            print(f"  {FAIL} {mod_name} -- {e}")
            errors += 1
            continue

        for name in names:
            if not hasattr(mod, name):
                print(f"  {FAIL} {mod_name} missing: {name}")
                errors += 1

    if errors:
        print(f"  {FAIL} {errors} import error(s)")
        sys.exit(1)
    print(f"  {PASS} All imports validated successfully.")


def check_streamlit_entry():
    """Verify app.py contains st.set_page_config()."""
    print(f"\n{CHECK} Checking Streamlit entry point...")
    if not os.path.exists("app.py"):
        print(f"  {FAIL} ERROR: app.py not found!")
        sys.exit(1)
    with open("app.py", encoding="utf-8") as f:
        tree = ast.parse(f.read())
    calls = [
        n
        for n in ast.walk(tree)
        if isinstance(n, ast.Call)
        and getattr(n.func, "attr", None) == "set_page_config"
    ]
    if calls:
        print(f"  {PASS} st.set_page_config() found -- entry point OK")
    else:
        print(f"  {SKIP} WARNING: st.set_page_config() not found in app.py")


if __name__ == "__main__":
    # Move to project root and ensure it's on sys.path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    sys.path.insert(0, project_root)
    check_syntax()
    validate_imports()
    check_streamlit_entry()
    print(f"\n{PASS} All lint checks passed.")
