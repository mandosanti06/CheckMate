# Contributing to CheckMate

Thanks for your interest in improving CheckMate. This project is alpha; we welcome small fixes and focused features.

## Setup

Clone the repo. The CLI itself has no runtime npm dependencies, so no `npm install` is required to use it.

For the Python runtime:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Running tests

```bash
npm run check
```

This runs the Node test suite (`node --test`) and the Python unittest suite.

## Scope

- Bug fixes and small features are welcome via pull request.
- Larger changes (new agent pieces, schema redesigns, CLI rewrites) should start as a discussion issue so we can align on direction before code review.
- Keep dependencies at zero where possible. New runtime npm dependencies require strong justification.

## Editing the skill bundle

The skill source lives at `skills/checkmate-agent-system/`. Edit files there directly. The distributable zip at `dist/checkmate-agent-system-skill.zip` is regenerated automatically:

- On `npm pack` / `npm publish` (via the `prepack` script).
- On demand with `npm run build:zip`.

Do not commit ad-hoc edits to the zip; always edit the source tree.

## Style

- Match existing code style.
- No emojis in code, comments, or docs.
- Keep comments minimal; explain the "why" when it isn't obvious from the code.
