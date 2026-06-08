# Contributing

Thanks for your interest in contributing to this project.

## How to contribute

1. Fork the repository and create a new branch for your change.
2. Make your changes and verify they work locally.
3. Commit with a clear, descriptive message.
4. Open a pull request with a short summary of the change.

## Local development

- Use the provided virtual environment or create your own:

```powershell
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

- Run Python syntax checks locally:

```powershell
python -m py_compile **\*.py
```

- If using PowerShell, confirm SQL Server setup helpers with:

```powershell
.\run_setup_sqlserver.ps1 --help
```

## Reporting issues

If you find a bug or want to request a feature, open an issue with:

- a clear title
- a description of what you expected
- steps to reproduce the problem
- any relevant logs or error messages

## License

By contributing, you agree that your contributions will be licensed under the project's MIT License.
