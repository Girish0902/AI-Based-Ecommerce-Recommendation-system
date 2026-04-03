"""Shared project-level configuration."""
import os

# Absolute path to the root of the project (one level up from this file)
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Absolute path to the main dataset CSV
DATA_PATH = os.path.join(PROJECT_ROOT, "cleaned_data.csv")
