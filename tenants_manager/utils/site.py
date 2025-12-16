import os
import json
import shutil
import subprocess
from pathlib import Path

import frappe
from frappe.utils import get_bench_path

def write_config_to_temp(site_name, config, validate=True):
    site_config_path = os.path.join(
        get_bench_path(), "sites", f"{site_name}.config.json"
    )
    """Update a value in site.config.json"""
    _file = Path(site_config_path)
    if not _file.is_file():
        _file.touch()
    with open(site_config_path, "w") as f:
        f.write(json.dumps(config, indent=1, sort_keys=True))


def delete_temp_config(site_name):
    """delete temp config"""
    site_config_path = os.path.join(
        get_bench_path(), "sites", f"{site_name}.config.json"
    )
    _file = Path(site_config_path)
    if _file.is_file():
        _file.unlink()


def clean_failed_site_creation(site_name, db_pass):
    delete_temp_config(site_name)
    cmd = ["bench", "drop-site", "--root-password", db_pass, site_name]
    try:
        # Try to delete from database
        p = subprocess.run(cmd, capture_output=True, cwd=get_bench_path())
    except Exception as e:
        pass

    site_path = os.path.join(get_bench_path(), "sites", site_name)
    try:
        # Try to delete site folder
        shutil.rmtree(site_path)
    except:
        pass
