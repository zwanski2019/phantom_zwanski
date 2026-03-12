"""Streamlit entrypoint shim for deployment."""

# Importing the app module triggers Streamlit UI construction at module load time.
import phantom_zwanski  # noqa: F401
