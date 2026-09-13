# Changelog

## Unreleased

- **Full validation-path composability (Soft #10):** `Validator` assembles concern units (`_ValidationPath`) instead of 11-way inherit. Exclusive / inverted bounds go through `_reject_exclusive` / `_configure_value` / `_configure_length` (`_all_specified`, None-only). Double-call and aggregate+leaf paths fail closed. `StringValidator` min-bound uses `_enforce_min_bound`. Public kwargs / README usage KEEP. Soft #8/#9 KEEP. Regex / rule / dual-schema untouched.
- **Composable Value/Length (Soft #9):** `ValueValidator` / `LengthValidator` compose leaf min/max validators instead of dual-inheriting them. Mutual-exclusion and conflicting-bound checks use `_all_specified` (`all(bound is not None for bound in bounds)`) so `0` stays a bound. Public constructors and attributes KEEP. Soft #8 bound honesty KEEP.
- **Bound honesty:** `0` is a bound, not unset — gates use `is not None` only (`min_value` / `max_value` / `eq` / `value` / `min_length` / `max_length` / `length` / `multiple_of`). `gt` / `lt` are exclusive (`>` / `<`); `min_value` / `max_value` stay inclusive (`>=` / `<=`); `eq` / `value` stay equality. No exclusive length aliases exist; length `0` is kept the same way. `MultipleValidator` remainder means multiple-of (`value % n == 0`; `multiple_of=0` only accepts `0`).
- **TaskValidator / `_processing`:** processing funcs run in `Validator._processing`; tasks run once in `TaskValidator` after `super()`, which now returns the processed value. `_job` caches by `id(tasks)` so default `cache_task=True` no longer TypeErrors.
- **E18 / P1:** `ExpiryValidator` pattern-checks `expire_before` itself and includes `expire_after` in the empty-bound test.
- **E16 / P1:** `ValueValidator` compares min/eq/max only when both sides are set, and binds `lt`/`gt`/`eq` with `is None` so `0` is kept. `DecimalValidator.value` annotation is `DECIMAL` (was `DEBUG`).
- **E15 / P1:** Named validators call their check directly. `validate()` no longer `add_validator`s itself on every assignment.
- **E14 / P0:** `Property.__set__` applies `default` only when the assigned value is `None`. Assigned `0`, `False`, and `""` are no longer replaced.
- **E13 / P0:** `is_valid_payment_card` now uses the in-tree brand helpers. A Luhn-valid `scanString` generator is no longer treated as a valid card.
