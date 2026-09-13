# Changelog

## Unreleased

- **TaskValidator / `_processing`:** processing funcs run in `Validator._processing`; tasks run once in `TaskValidator` after `super()`, which now returns the processed value. `_job` caches by `id(tasks)` so default `cache_task=True` no longer TypeErrors.
- **E18 / P1:** `ExpiryValidator` pattern-checks `expire_before` itself and includes `expire_after` in the empty-bound test.
- **E16 / P1:** `ValueValidator` compares min/eq/max only when both sides are set, and binds `lt`/`gt`/`eq` with `is None` so `0` is kept. `DecimalValidator.value` annotation is `DECIMAL` (was `DEBUG`).
- **E15 / P1:** Named validators call their check directly. `validate()` no longer `add_validator`s itself on every assignment.
- **E14 / P0:** `Property.__set__` applies `default` only when the assigned value is `None`. Assigned `0`, `False`, and `""` are no longer replaced.
- **E13 / P0:** `is_valid_payment_card` now uses the in-tree brand helpers. A Luhn-valid `scanString` generator is no longer treated as a valid card.
