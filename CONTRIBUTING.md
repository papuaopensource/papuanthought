# Contributing

Thank you for taking the time to contribute. This project is open to anyone who wants to help build a digital space for Papuan voices.

## Reporting Issues

Use the Issues feature on the GitHub repository to report bugs or propose new features. Include steps to reproduce the issue where possible.

## Contribution Workflow

Fork the repository, then create a new branch from `main`.

Branch naming:

- `feat/feature-name` for new features
- `fix/fix-name` for bug fixes
- `docs/change-name` for documentation changes

Make your changes, ensure the project still runs correctly, then submit a pull request to the `main` branch.

## Code Standards

**Views** — All views are written as Class-Based Views (CBVs). Function-based views are not used.

**Business logic** — Place it in each app's `services.py`. Views only call functions from services.

**Migrations** — Always include migration files when changing a model.

**Comments** — Write them only when something is not obvious from the code itself.

## Commit Messages

This project follows the [Conventional Commits](https://www.conventionalcommits.org) convention.

Format:

```
<type>(<scope>): <short description>
```

Common types:

- `feat` — new feature
- `fix` — bug fix
- `docs` — documentation changes
- `refactor` — code change without adding a feature or fixing a bug
- `style` — visual or formatting changes
- `chore` — maintenance, configuration, dependencies

Examples:

```
feat(posts): add note editing
fix(notifications): correct unread badge count on reload
docs(readme): update local setup instructions
refactor(interactions): extract tag helper into shared function
```

## Questions

Reach out to the Papua Open Source team via the contact page on the platform or open a discussion in the GitHub repository.
