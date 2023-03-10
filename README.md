<img src="static/asuna-icon.png" alt="Asuna" width="300" />

# Asuna

🗡️A code coverage report tool for your project.

## Features

- Create project for store your coverage report
- Upload coverage report via GitHub action
- Rich rendered coverage report

## Supported coverage report

- [Python (coverage.py)](https://coverage.readthedocs.io/)
- [Node.js (Istanbul)](https://istanbul.js.org/)

## Using Asuna with your project

More info in [wiki](https://github.com/HelloYeew/asuna/wiki)

## Start developing asuna

This project required

- [Python 3.11](https://www.python.org/downloads/)
- [Poetry](https://python-poetry.org/docs/#installation)

Copy `.env.example` to `.env` and fill the value

```bash
cat .env.example > .env
```

Install dependencies

```bash
poetry install
```

Migrate database

```bash
poetry run python manage.py migrate
```

Run server

```bash
poetry run python manage.py runserver
```

If you want to stay in the poetry shell, you can run

```bash
poetry shell
```

## Contributing

Currently this project is much ready now but not available for some feature like collaboration. 
If you have any idea or want to contribute, feel free to open an issue or pull request!
