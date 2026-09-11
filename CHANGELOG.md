# Changelog

## Unreleased

- **E14 / P0:** `Property.__set__` applies `default` only when the assigned value is `None`. Assigned `0`, `False`, and `""` are no longer replaced.
- **E13 / P0:** `is_valid_payment_card` now uses the in-tree brand helpers. A Luhn-valid `scanString` generator is no longer treated as a valid card.
