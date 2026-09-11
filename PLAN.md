# Valio honesty map (TELOS) + cut order (Ponytail)

Same product. Framework Lock held. This is the map. It is not a new validation
framework, not a public rename, not a docs rewrite, not a sibling package.

Probed on `main` @ `5a574a5` (Python 3.12, installed `typingx` / `phonenumbers` /
`pyparsing`). Existing suite: **3 failed, 38 passed**.

## Framework Lock (KEEP)

Valio is a **descriptor-on-dataclass** validator: assign → `Property.__set__` →
`pre_set` / `validate` / store / `post_set`. `debug=True` raises; `debug` falsy
swallows and leaves the attribute unset (readback `None`). That silent path is
documented in README and locked by `valio/tests/validator/test_validators.py`.
Do not flip the default to fail-closed.

Locked public names (do not rename for cleanliness):

- `Validator`, `*Validator`, `*Field`, `Property`, `Pattern` / combinators
- `add_validator`, `add_pre_validator`, `add_post_validator`, `enable_async`
- PyPI / import name `valio`

Product job: plug constraints onto dataclass fields; named ID/card/phone/email
validators must enforce their namesake when `debug=True`.

## Kill list (do not do)

- Fashion folders (`docs/`, `src/valio/`, new `core/` / `api/`)
- Textbook overlays (new regex DSL, mypy-formatter port, Luhn-mod-N essay)
- Sibling packages (new `valio-schema`, `dust`, extra pyproject)
- Public rename for cleanliness
- Docs-first README/PyPI rewrite without a code fix in the same concern
- Inventing a nicer validation framework

## Layers

| Layer | What is true on `main` |
| --- | --- |
| **CLAIMED** | PyPI/README: dataclasses, async validation, async tasks, extension hooks, regex, dynamic docs, `Validator.register(User)`, `add_pre_valiator`, named Aadhaar/Phone/Email/PaymentCard/Date |
| **EXPORTED** | `valio/__init__.py` star-imports descriptor, error, logger, regexer, schema **v2**, validator, field. Includes `DustError`, Schema v2 types, Pattern combinators |
| **IMPLEMENTED** | Descriptor cycle works. Type/required/pattern/reassign/length/value/choice/expiry run. Named validators exist. Field is a constructor wrapper. Schema v2 subclasses Field. Logger writes files when `logger is not False` |
| **LOCKED** | Names above + `debug` swallow + dataclass assignment + installed deps (`typingx`, `phonenumbers`, `pyparsing`) |

## Rank

**DO** = E13 / P0 / P1 only (this pass).
**KEEP** = leave; lock or not worth the break.
**DEAD** = do not implement; delete later, not in a bug PR unless leftover in the touched file.

### DO — this pass (one PR each)

| ID | Rank | Gap | Evidence | Cut |
| --- | --- | --- | --- | --- |
| **E14** | **P0** | `Property.__set__` uses `value or default`. Falsy assigned values are replaced. Data loss for every field with a default. | `descriptors.py` ~263–264. Probe: `IntegerValidator(default=5, debug=True)` → `N(n=0).n == 5`. Same for `BooleanValidator(default=True)` + `False`, `StringValidator(default='fallback')` + `''` | One line: apply default only when `value is None`. Tests for `0` / `False` / `''` with default |
| **E13** | **P0** | `PaymentCardValidator` claims card validation. `is_valid_payment_card` is `luhn and Regex(...).scanString(...)`. `scanString` returns a **generator**, always truthy. Any Luhn-valid digit string passes, including `0000000000000000` and `79927398713`. Brand matchers already do Luhn + `re_match`. | `paymentcards.py` 110–112 vs 85–107. Probe: `PaymentCardValidator(debug=True)` accepts both non-brand Luhn numbers; rejects only Luhn-fail `4111111111111112` | Reuse in-tree brand helpers (`is_card_of_*`). No new card scheme |
| **E15** | **P1** | Named validators call `self.add_validator(...)` **inside** `validate()`. Each assignment appends another copy. Grows without bound; runs N times on the Nth set. | `validators.py` Hex/Payment/Phone/Path/IP/Aadhaar/PAN `validate`. Probe: shared `HexColorValidator`, 3 assigns → custom list length 1, 2, 3 | Call the check directly; stop registering on every validate. Same for every named validator that does this |
| **E16** | **P1** | `ValueValidator.__init__`: `if max_value is not None or value is not None: max_value < value` TypeErrors when only one side is set. Also `max_value or lt` / `value or eq` drop `0`. Hits every `Validator` subclass. `DecimalValidator.value` annotated `DEBUG`. | `validators.py` 753–770, 1665. Probe: `ValueValidator(value=1)` → `TypeError: '<' not supported between instances of 'NoneType' and 'int'` | Compare only when **both** are not `None`. Bind aliases with `is None`, not `or`. `value: DECIMAL` |
| **E18** | **P1** | `ExpiryValidator`: `expire_before` string pattern check uses `isinstance(expire_after, str)`. `any([expire_before, expire_on, expire_before])` never mentions `expire_after`. | `validators.py` 1004, 1028 | Check `expire_before`; include `expire_after` in the empty test |

### KEEP

| ID | Why |
| --- | --- |
| K1 | `debug` falsy swallow → `None`. README + tests. Trust-boundary *default* is locked; do not “fix” by changing the default |
| K2 | `Validator.register` is stdlib `ABC.register`, not a product API. README example is cargo-cult. Do not invent `register()` |
| K3 | `add_pre_validator` is the real name. Do not add `add_pre_valiator` alias |
| K4 | Pattern `findall` (substring). Tests accept `"a string"` for `r'\w+'`. Do not switch to `fullmatch` in this pass |
| K5 | Public class / hook names. No rename pass |
| K6 | `typingx` / `phonenumbers` / `pyparsing` already installed. Do not add deps |
| K7 | Field / Schema v2 wrappers. Duplicate constructors are ugly; not a P0 lie |
| K8 | Tests living under `valio/tests` and `valio/regexer/tests`. Do not move for fashion |
| K9 | `enable_async` / `TaskValidator` (`asyncio.run` in the setter). Claimed async is weak; rewriting it is a new framework. Out of this pass |
| K10 | Logger writes files when `logger is not False` (default `None` enables). Footgun, not this pass |
| K11 | `min_value is not None and self.min_value` treats `0` as unset in several `_validate_*` methods. Sibling of E14; only fix if it rides a DO PR’s root cause. Do not sweep the file |

### DEAD (do not build; delete later, not as a “cleanup” PR for its own sake)

| ID | What | Why dead |
| --- | --- | --- |
| D1 | `valio/logger/color_format.py` (547 lines) | Unused mypy textbook overlay (`MYPY_FORCE_COLOR`, `FancyFormatter`). Not imported. `typing_extensions` not in deps |
| D2 | `valio/schema/schemas.py` | Import commented out; v2 is the live export. Sibling leftover |
| D3 | `DustBaseException` / `DustError` | Sibling-package names, exported via star-import, unused |
| D4 | `profile` / `timed_lru_cache` in `validators.py` | Unused teaching / commented cache |
| D5 | `schemas_v2.py` / `schemas.py` `if __name__ == "__main__"` password demos | Leftover teaching |
| D6 | `PositiveIntegerSchema` etc. in v1 only | Unexported after v2 switch |
| D7 | PAN module’s Luhn-mod-N essay + unused `verify`/`generate` | Textbook overlay; `is_valid_pan_number` is regex `findall` only |
| D8 | New schema package / new public API surface | Sibling package |

## Honesty gaps (CLAIMED / EXPORTED / IMPLEMENTED / LOCKED)

| Claim or export | Status |
| --- | --- |
| Dataclass field validators | IMPLEMENTED + LOCKED |
| Named Email/Phone/Aadhaar/PAN/Date | EXPORTED; Email/Date use `findall`; Phone uses `phonenumbers`; Aadhaar Verhoeff looks real; **PaymentCard IMPLEMENTED as Luhn-only (E13)** |
| `Validator.register(User)` creates a User validator | CLAIMED, not IMPLEMENTED (ABC.register). KEEP |
| `add_pre_valiator` | CLAIMED typo; EXPORTED is `add_pre_validator` |
| Async validation / tasks | EXPORTED `enable_async`, `add_*_task`; IMPLEMENTED via `asyncio.run` + executor wrap. KEEP this pass |
| Dynamic documentation | IMPLEMENTED: `__set_name__` appends to `owner.__doc__` |
| Schema | EXPORTED v2 only; v1 DEAD in-tree |
| `Dust*` | EXPORTED, not IMPLEMENTED as valio |
| `color_format` | in-tree, not EXPORTED from `valio.logger` |

## Existing test failures on `main` (not this pass unless they share a DO root cause)

1. `TestPropertyClass.test_property_assigned_class` — `__doc__` string drift (`NoneType` vs current typing).
2. `TestTypeValidator.test_type_class_validator` — reused validator + `Union` annotation vs `issubclassx` (test itself documents the collision).
3. `regex_test.test_preceded_by` — expected email-special set vs `special_chars` (ASCII 32–47). Test/overlay mismatch.

Do not “fix” tests to match fashion. Only touch if a DO PR changes the behavior they assert.

## Cut order

1. **This plan PR** — map only.
2. **E14 / P0** — `Property.__set__` default only when `value is None`.
3. **E13 / P0** — `is_valid_payment_card` reuse brand helpers.
4. **E15 / P1** — named `validate()` must not `add_validator` itself.
5. **E16 / P1** — `ValueValidator` both-sides compare + `is None` aliases.
6. **E18 / P1** — `ExpiryValidator` copy-paste.

Stop. No README pass, no folder moves, no async rewrite, no DEAD deletions unless they sit in a file already opened for a DO fix.

## Per-PR completeness

Each DO PR: code + the smallest test that fails if the lie returns + leftover teaching in the touched hunk + a `CHANGELOG.md` bullet (create the file on the first fix PR). One concern. No extra helpers.

## Verify (tip each fix PR with these)

**E14**

```bash
python -m pytest valio/tests/descriptor/test_descriptors.py valio/tests/validator/test_validators.py -q
python - <<'PY'
from dataclasses import dataclass
from valio import IntegerValidator, BooleanValidator
@dataclass
class N:
    n: int = IntegerValidator(default=5, debug=True, logger=False)
    flag: bool = BooleanValidator(default=True, debug=True, logger=False)
assert N(n=0).n == 0
assert N(flag=False).flag is False
assert N().n == 5
print('e14 ok')
PY
```

**E13**

```bash
python - <<'PY'
from dataclasses import dataclass
from valio import PaymentCardValidator
@dataclass
class C:
    c: str = PaymentCardValidator(debug=True, logger=False)
assert C(c='4111111111111111').c == '4111111111111111'
for bad in ('0000000000000000', '79927398713', '4111111111111112'):
    try:
        C(c=bad)
    except ValueError:
        continue
    raise SystemExit('e13 still accepts ' + bad)
print('e13 ok')
PY
```

**E15**

```bash
python - <<'PY'
from dataclasses import dataclass
from valio import HexColorValidator
v = HexColorValidator(debug=True, logger=False)
@dataclass
class H:
    h: str = v
H(h='#fff'); H(h='#ffffff'); H(h='#abc')
assert all(len(fns) <= 1 for fns in v._custom_validators.values()), v._custom_validators
print('e15 ok')
PY
```

**E16**

```bash
python - <<'PY'
from decimal import Decimal
from valio.validator.validators import DecimalValidator, ValueValidator
DecimalValidator(debug=True, logger=False, value=Decimal("1"))
ValueValidator(value=1, debug=True, logger=False)  # must not TypeError
ValueValidator(value=0, max_value=10, debug=True, logger=False)
print('e16 ok')
PY
```

**E18**

```bash
python - <<'PY'
from valio.validator.validators import ExpiryValidator
e = ExpiryValidator(expire_before='2020-01-01', debug=True)
assert e.timeline == 'before'
print('e18 ok')
PY
```
