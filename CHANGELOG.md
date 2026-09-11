# Changelog

## Unreleased

- **E14 / P0:** `Property.__set__` applies `default` only when the assigned value is `None`. Assigned `0`, `False`, and `""` are no longer replaced.
