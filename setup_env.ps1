# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
python -m venv venv_backup
.\venv_backup\Scripts\Activate.ps1
pip install -r .\requirements.txt