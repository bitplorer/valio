# ux-valio source map (Evidence Pack)

Read-only cartography of `https://github.com/bitplorer/valio` at `main`.
No product code in this branch. This map is for a greenfield repo named `ux-valio`.
It is not a Soft patch plan.

**Tip (measured).** `git rev-parse origin/main` = `3415c03e37085adda4040671a91eb19aa4fe4ac4`
(`Soft 10: compose full validation path; fail-closed units (#10)`).

**Pre-Soft baseline (measured).** `5a574a55fea1621506b499e33cb84302837f4555` (`Bumped Version`).
The closed honesty map at `origin/cursor/telos-honesty-map-e4a4:PLAN.md` (PR #1, closed) was written against that SHA. Soft #2 through #10 landed after it. Treat PLAN.md as history, not as current truth.

**Cap / mount_channel.** `git grep` on `HEAD` for `mount_channel`, `Cap Host`, and `cap.host` returns nothing. No `rule/` folder. No `examples/` folder. Do not invent those Softs.

**Tree (measured).** `git ls-tree -r --name-only origin/main` has 48 paths. Product lives under `valio/`. Docs on `main` are `README.md`, `CHANGELOG.md`, `LICENSE`. There is no `docs/` on `main`.

```
git log --oneline origin/main | head -10
3415c03 Soft 10: compose full validation path; fail-closed units (#10)
14d253e Soft 9: readable mutual-exclusion + composable Value/Length (#9)
7fb0513 Soft 8: bound honesty (0 is a bound; gt/lt exclusive) (#8)
4c3d0dd Fix TaskValidator inheritance so tasks run once after processing. (#7)
a647ad1 Fix P1: ExpiryValidator must pattern-check expire_before. (#6)
eb4ce37 P1: ValueValidator must not compare a missing bound (#5)
51f7df1 Fix P1: named validators must not register themselves on each assign. (#4)
e8284b6 Fix P0: payment cards must match a brand, not a live generator. (#3)
b2b17c6 Fix P0: keep assigned falsy values when a default is set. (#2)
5a574a5 Bumped Version
```

Merge SHAs (from `gh pr view` + `git log`):

| PR | Title | merge SHA |
| --- | --- | --- |
| #7 | Fix TaskValidator inheritance so tasks run once after processing | `4c3d0dd5cfc640183f3e068bf54c495becd43a0c` |
| #8 | Soft 8: bound honesty (0 is a bound; gt/lt exclusive) | `7fb0513bee93f6423fda9e55e8f4fbfd581a03c0` |
| #9 | Soft 9: readable mutual-exclusion + composable Value/Length | `14d253ec569b77d8a7bc9a99cad72f0634d6e7dd` |
| #10 | Soft 10: compose full validation path; fail-closed units | `3415c03e37085adda4040671a91eb19aa4fe4ac4` |

## 1. Core generating idea

Valio is a descriptor that sits on a dataclass field and runs constraints when Python assigns a value.
`Property.__set__` (`valio/descriptor/descriptors.py:253`) applies `default` only when the assigned value `is None` (`:262`, Soft #2 / E14), then calls `pre_set`, stores `obj.__dict__[self.name]`, then `post_set`.
Only the `pre_set` return is stored. `post_set` / `pre_get` / `post_get` / delete return values are ignored (`descriptors.py:264-268`, `:287-300`).
`__get__` and `__delete__` pass `self.name` into processing, not the stored value (`descriptors.py:287`, `test_task_processing_order.py:76-77` log `("pget_proc", "x")`).
`ValidateProperty.pre_set` (`valio/validator/validators.py:182`) runs `pre_validation_processing`, then abstract `validate`, then `post_validation_processing`.
`debug=True` re-raises. `debug` falsy swallows the exception, appends it to `self.errors`, and leaves the attribute unset so later `__get__` reads `None` (`descriptors.py:269-274`, locked by `valio/tests/validator/test_validators.py:55-69`).
Leaf class attributes such as `required: BOOL = TypeValidator(...)` (`validators.py:418`) mean constructor kwargs are themselves descriptor-validated.
The product job, from README plus that cycle, is plug-in constraints on dataclass fields (type, required, pattern, bounds, named ID/card/phone/email checks) with optional processing hooks and file logging.
It is not a pydantic-style model class, not a schema DSL in the live export, and not a fail-closed-by-default parser.

README title (`README.md:1`) calls it a "Progressive Validation Library" that "goes along with dataclasses".
`pyproject.toml:4` claims "Pluggable validation library that supports dataclasses, async validation, async tasks, validation extension, regex validation, dynamic documentation and much more."
The live mechanism that makes those claims true or false is the descriptor cycle above, not Soft chat.

## 2. Four inventories

Status words. **CLAIMED** = README / PyPI description / docstring. **EXPORTED** = importable via `from valio import *` or the star-import chain. **IMPLEMENTED** = code that runs. **LOCKED** = a test asserts it.

### CLAIMED

| Claim | Cite | Honesty on tip |
| --- | --- | --- |
| Dataclass field validators | `README.md:22-46`, `pyproject.toml:4` | IMPLEMENTED + LOCKED |
| Named Aadhaar / Phone / Email / PaymentCard / Date | `README.md:27-45` | EXPORTED. Phone uses `phonenumbers` (`validators.py:64`, `:2262`). PaymentCard uses brand helpers (Soft #3). Email/Date use `re.findall` substring match (`:2181`, `:2144`). Aadhaar calls `relib.is_valid_aadhaar_card`. No dedicated Email/Phone/Aadhaar/Date tests. |
| `Validator.register(User)` builds a User validator | `README.md:51` | CLAIMED only. `Validator` subclasses `ValidateProperty` which subclasses `ABC` (`validators.py:171`). `register` is stdlib `ABC.register`. |
| `add_pre_valiator` decorator | `README.md:79` | Typo. Real name is `add_pre_validator` (`fields.py:128`, `validators.py:1860`). |
| Async validation and async tasks | `pyproject.toml:4`, `enable_async` (`validators.py:1698`, `:1782`) | IMPLEMENTED via `asyncio.run` + `async_wrap` executor (`:1956-1968`). Not LOCKED. |
| Regex out of the box, including pyparsing `Regex` | `README.md:137-170` | Pattern combinators IMPLEMENTED. pyparsing is a match helper in relib (see HOLD). |
| `debug=True` throws, else defaults to None | `README.md:47-48` | IMPLEMENTED + LOCKED (`test_validators.py:55-69`) |
| `logger=True` logs the field to a separate file | `README.md:47` | IMPLEMENTED when `logger is not False` (`descriptors.py:235`, `loggers.py:29`). Default `logger=None` enables logging (footgun). Not LOCKED. |
| Field decorator hooks (`add_pre` / `add_post` / `add_validator`) | `README.md:79-125` | IMPLEMENTED on `FieldMixin` (`fields.py:124-182`) as pass-through to the constructed validator. No Field tests. |
| Dynamic documentation | `pyproject.toml:4` | IMPLEMENTED. `__set_name__` appends to `owner.__doc__` (`descriptors.py:204-230`). LOCKED poorly. `test_property_assigned_class` fails on module-path drift. |
| Schema | not in README. Exported via `valio/schema/__init__.py` | v2 EXPORTED. v1 parked. Neither LOCKED. |
| Version `0.1.0b6` | `pyproject.toml:3`, `valio/__init__.py:16` | LOCKED (`test_validators.py:19-20`) |

README happy-path snippets that tests re-lock after Soft #9/#10:

- `StringValidator(..., max_length=50, required=True)` (`README.md:39`, `test_soft10_validation_path.py:175`)
- `Validator(in_choice=[...], default="Female")` (`README.md:45`, choice locked without default at `test_soft10_validation_path.py:219`)
- `StringField(min_length=6, max_length=30)` (`README.md:66-76`). Field wrapper itself is not tested. Validator kwargs are.

README is missing imports it uses (`datetime`, `typing`, `Pattern`, `bcrypt`). Those are docstring rot, not APIs.

### EXPORTED

Star-import chain (`valio/__init__.py:7-14`):

```
from .descriptor import *   # descriptors.py __all__
from .error import *        # errors.py, no __all__ (all public names)
from .logger import *       # loggers.py __all__ only. color_format is not imported
from .regexer import *      # regexps.py __all__ + relib star-imports
from .schema import *       # schemas_v2 only (`schema/__init__.py:8-9`)
from .validator import *    # validators.py __all__
from .field import *        # fields.py __all__
```

**descriptor `__all__`** (`descriptors.py:17`). `Property`, `NAME`, `DEFAULT`, `DOC`, `DEBUG`.

**validator `__all__`** (`validators.py:71-126`). `ValidateProperty`, `TypeValidator`, `RequiredValidator`, `PatternValidator`, `ReassignValidator`, `MultipleValidator`, `ValueValidator`, `LengthValidator`, `ExpiryValidator`, `ChoiceValidator`, `TaskValidator`, `Validator`, typed aliases (`IntegerValidator` through `TupleValidator`), and type aliases `INT` `FLOAT` `BYTES` `BOOL` `STR` `PATTERN` `VALUE` `DATE_TIME_DELTA` `TYPE` `UUID_Type` `CHOICE`.

Not in `__all__` (importable from `valio.validator.validators`, not via `from valio import *`): `MinValueValidator`, `MaxValueValidator`, `MinLengthValidator`, `MaxLengthValidator`, `AttributeValidator`, `_ValidationPath`, `_all_specified`, `DECIMAL`, `profile`, `timed_lru_cache`, `async_wrap`.

**field `__all__`** (`fields.py:20-42`). `FieldMixin`, `Field`, typed `*Field`. Not `FieldBase`.

**schema v2** (`schemas_v2.py`). No `__all__`. Live export is `Schema`, `BytesSchema`, `BooleanSchema`, `NumberSchema`, `IntegerSchema`, `FloatSchema`, `CharSchema`, `DateSchema`, `FileSchema`. v1 extras (`PositiveIntegerSchema`, `EmailSchema`, `PaymentCardSchema`, `PhoneNumberSchema`, `SchemaMixin`) are not exported (`schema/__init__.py:8` comments out `schemas.py`).

**error** (`errors.py`). No `__all__`. `SetPropertyError`, `GetPropertyError`, `DeletePropertyError`, `SetAttributeError`, `GetAttributeError`, `DeleteAttributeError`, `DustBaseException`, `DustError`.

**logger `__all__`** (`loggers.py:14`). `Logger`, `LOGGER`, `LOG_LEVEL`, `LOG_DIR`. `color_format.py` is in-tree and unused (no import).

**regexer `__all__`** (`regexps.py:12-35`). `PatternType`, `Pattern`, `All`, `Any`, `SetOf`, `Escape`, capturing groups, lookarounds, `StartOfString`, `EndOfString`, `WordBoundary`, and related combinators. Relib re-exports brand helpers, color patterns, date patterns, `is_valid_aadhaar_card`, `is_valid_pan_number`, `is_valid_payment_card`.

### IMPLEMENTED

Live assignment path (tip):

1. Dataclass field default is a `Property` subclass instance (`StringValidator`, `Validator`, or `some_field.validator`).
2. `__set_name__` sets `name`, matches `annotation` via `typingx.issubclassx` (`descriptors.py:174`), appends owner docstring (`:204`).
3. `__set__` default-if-None (`:262`), `pre_set` (`:264`), store (`:265`), `post_set` (`:268`). `debug` gates re-raise (`:273`).
4. `ValidateProperty.pre_set` (`validators.py:182`) processing then `validate` then processing.
5. `Validator.validate` (`:1780`) runs `_validate_field` unless `enable_async`.
6. `_validate_field` (`:1793`) runs `_validation_path` then `_custom_validators`.
7. Default path names (`:1631-1642`). `reassignment`, `type`, `required`, `pattern`, `multiple_of`, `length`, `value`, `expiry`, `choice`, `attribute`.
8. Processing hooks run in `_processing` (`:1835`). Tasks run after via `_after_processing_run_tasks` (`:807`, Soft #7).

Concern leaves still exist as classes. Soft #10 `Validator` no longer inherits them. It aliases leaf `_validate_*` methods (`:1644-1668`) and copies task helpers from `TaskValidator`.

`Field` is a constructor wrapper, not a descriptor. `Field.__init__` (`fields.py:218`) builds `self.validator = self.validator(...)`. README then assigns `user: User = user_field.validator` (`README.md:127`). Schema v2 subclasses `Field` (`schemas_v2.py:21`) and does the same in its `__main__` demo (`:196`).

### LOCKED

See section 9. Soft #8 bound honesty must not regress. Soft #2 falsy defaults, #3 payment brand, #4 named-validate-once, #5 one-sided value init, #6 expiry `expire_before`, #7 task order, #9 compose-not-inherit + `_all_specified`, #10 path fail-closed are LOCKED by dedicated files.

Not LOCKED on tip. Schema, Field wrappers, `enable_async`, `has_attributes`, Path/IP/UUID/Enum/Aadhaar/PAN/Email/Phone/Date validators, logger files, `DustError`, Pattern combinators beyond `regex_test.py`, pyparsing usage.

Pre-existing failures on tip (same as PLAN.md at `5a574a5`, still red after Soft #10). Measured `python3 -m unittest discover -s valio/tests -t .`. 111 tests, 1 fail, 1 error.

1. `TestPropertyClass.test_property_assigned_class`. Docstring `__main__.PropertyClass` vs `valio.tests.descriptor.test_descriptors.PropertyClass`.
2. `TestTypeValidator.test_type_class_validator`. Reused `TypeValidator` + `Union` vs `issubclassx` raises `TypeError` (test expected `RuntimeError`).

Regexer pytest. 3 passed, 1 failed. `test_preceded_by` expected email-special set vs `special_chars` ASCII 32-47 (`regex_test.py:167`).

## 3. Full public surface

### Modules

| Module | Path | Role |
| --- | --- | --- |
| package | `valio/__init__.py` | star-import barrel + `__version__` |
| descriptor | `valio/descriptor/descriptors.py` | `Property` descriptor + logging mix-in base |
| validator | `valio/validator/validators.py` | constraints, facades, named IDs, tasks |
| field | `valio/field/fields.py` | factory wrappers around validator ctors |
| schema v2 | `valio/schema/schemas_v2.py` | `Schema(Field)` + typed schemas |
| schema v1 | `valio/schema/schemas.py` | parked. import commented out |
| regexer | `valio/regexer/regexps.py` | Pattern combinators (`&`, `\|`) |
| relib | `valio/regexer/relib/*.py` | named patterns and ID helpers |
| logger | `valio/logger/loggers.py` | file logger |
| color_format | `valio/logger/color_format.py` | unused mypy-style formatter |
| error | `valio/error/errors.py` | property errors + `Dust*` |

### Classes (validators.py, with bases on tip `3415c03`)

Every concern leaf subclasses `ValidateProperty`. Facades do too. Typed aliases subclass `Validator`.

| Line | Class | Bases on tip |
| --- | --- | --- |
| 171 | `ValidateProperty` | `descriptors.Property`, `ABC` |
| 359 | `TypeValidator` | `ValidateProperty` |
| 417 | `RequiredValidator` | `ValidateProperty` |
| 461 | `PatternValidator` | `ValidateProperty` |
| 516 | `ReassignValidator` | `ValidateProperty` |
| 570 | `MultipleValidator` | `ValidateProperty` |
| 820 | `_ValidationPath` | (plain class, not exported) |
| 868 | `MinValueValidator` | `ValidateProperty` |
| 915 | `MaxValueValidator` | `ValidateProperty` |
| 984 | `ValueValidator` | `ValidateProperty` (Soft #9 retired min+max inherit) |
| 1076 | `MinLengthValidator` | `ValidateProperty` |
| 1124 | `MaxLengthValidator` | `ValidateProperty` |
| 1173 | `LengthValidator` | `ValidateProperty` (Soft #9 retired min+max inherit) |
| 1265 | `ExpiryValidator` | `ValidateProperty` |
| 1347 | `ChoiceValidator` | `ValidateProperty` |
| 1432 | `AttributeValidator` | `ValidateProperty` |
| 1476 | `TaskValidator` | `ValidateProperty` |
| 1581 | `Validator` | `ValidateProperty` (Soft #10 retired 11-way inherit) |
| 1971+ | `IntegerValidator` … `TupleValidator` | `Validator` or `StringValidator` |

Pre-Soft (`5a574a5`) bases, recovered with `git show 5a574a5:valio/validator/validators.py`:

```
class ValueValidator(MinValueValidator, MaxValueValidator):   # line 728
class LengthValidator(MinLengthValidator, MaxLengthValidator): # line 913
class Validator(                                               # line 1345
    TypeValidator, RequiredValidator, PatternValidator,
    ReassignValidator, MultipleValidator, ValueValidator,
    LengthValidator, ExpiryValidator, ChoiceValidator,
    AttributeValidator, TaskValidator):
```

Those three inherit lines are the architecture Soft #9/#10 papered over. They are gone on tip.

### Helpers (not exported)

| Line | Name |
| --- | --- |
| 129 | `profile` (unused) |
| 153 | `timed_lru_cache` (unused; commented cache on `_validate_field`) |
| 619 | `_all_specified` |
| 629 | `_reject_exclusive` |
| 635 | `_reject_inverted` |
| 641 | `_append_doc` |
| 651 | `_bound_attr` |
| 662 | `_enforce_min_bound` |
| 704 | `_configure_value` |
| 736 | `_configure_length` |
| 748 | `_configure_expiry` |
| 780 | `_init_task_state` |
| 794 | `_remember_assignment_start` / `_finish` |
| 807 | `_after_processing_run_tasks` |
| 1956 | `async_wrap` |
| 1967 | `main` (`asyncio.gather`) |

### Entry points

| Entry | Path |
| --- | --- |
| Dataclass assignment | `Property.__set__` `descriptors.py:253` |
| Class body bind | `Property.__set_name__` `:232` |
| Validate hook | `ValidateProperty.pre_set` `validators.py:182` |
| Facade validate | `Validator.validate` `:1780` |
| Custom checks | `add_validator` `:1828` |
| Processors | `add_pre_validator` / `add_post_validator` / `add_post_set` / get / delete `:1860-1953` |
| Tasks | `add_*_task` on `TaskValidator` and aliased on `Validator` `:1516-1549`, `:1662-1668` |
| Field decorators | `FieldMixin.add_*` `fields.py:124-182` |
| Pattern compose | `PatternType.__and__` / `__or__` in `regexps.py` (used by README `:152`) |

## 4. Feature catalog

| Capability | Owner | Path | Soft-patched? |
| --- | --- | --- | --- |
| Descriptor set/get/delete + debug swallow | `Property` | `descriptors.py:253-329` | #2 default-if-None only (`:262`) |
| Annotation match (`issubclassx`) | `Property._may_set_or_ensure_annotation_match` | `descriptors.py:157` | no. typingx HOLD |
| Type check (`isinstancex`) | `TypeValidator._validate_type` | `validators.py:403` | no. typingx HOLD |
| Required None-check | `RequiredValidator` | `:417` | no. still `is not None and self.required` (`:445`). For a bool this is the flag. Soft #8 did not touch it |
| Pattern `re.findall` (substring) | `PatternValidator` | `:489-512` | no. KEEP per PLAN K4 |
| Reassign-once | `ReassignValidator` | `:516`, helpers `:794-804` | #10 helpers extracted. behavior #7-adjacent |
| Multiple-of remainder | `MultipleValidator` | `:595-616` | **#8**. `%`; `multiple_of=0` accepts only `0` |
| Inclusive min / exclusive gt | `MinValueValidator` + `_enforce_min_bound` | `:868`, `:662` | **#8** honesty, **#10** shared helper |
| Inclusive max / exclusive lt | `MaxValueValidator` | `:915` | **#8** |
| Exact value / eq | `ValueValidator` | `:984` | **#5** both-sides compare, **#8** `0`, **#9** compose leaves |
| Inclusive min/max/exact length | `Min/Max/LengthValidator` | `:1076`, `:1124`, `:1173` | **#8** length `0`, **#9** compose |
| Expiry after/on/before | `ExpiryValidator` + `_configure_expiry` | `:1265`, `:748` | **#6** `expire_before` pattern, **#10** helper. leftover truthy `and self.expiry` (`:1296`) |
| Choice in / not in | `ChoiceValidator` | `:1347` | no. LOCKED via Soft #10 public-usage. leftover truthy `and self.in_choice` / `and self.not_in_choice` (`:1396`, `:1415`). empty list would skip |
| `has_attributes` | `AttributeValidator` | `:1432` | no. leftover truthy `and self.has_attributes` (`:1459`). empty list would skip. not LOCKED |
| Tasks (`asyncio.run` / cache by `id(tasks)`) | `TaskValidator` | `:1476`, `:1489` | **#7** |
| Processing funcs then tasks | `Validator._processing` + `_after_processing_run_tasks` | `:1835`, `:1850` | **#7**, **#10** (no inherit) |
| Ordered unique concern path | `_ValidationPath` | `:820` | **#10** |
| Fail-closed exclusive / inverted bounds | `_reject_exclusive`, `_reject_inverted` | `:629`, `:635` | **#9/#10** |
| Hex color fullmatch | `Hex*ColorValidator` | `:2030-2060` | **#4** stop `add_validator` inside `validate` |
| RGB/RGBA color | `RGBOrRGBAColorValidator` | `:2063` | #4. uses `relib.r_rgb \| r_rbga` (typo `rbga`) |
| HSL/HSLA color | `HSLOrHSLAColorValidator` | `:2075` | #4. **honesty hole**. `_validate_hsl_or_hsla_color_pattern` compiles `r_rgb \| r_rbga`, not `r_hsl \| r_hsla` (`:2082`) |
| Date pattern findall | `DateValidator` | `:2087` | no. local copy of `_validate_pattern` (`:2132`). non-str becomes `None` instead of `str(value)` |
| Field factory + decorator door | `Field` / `*Field` | `fields.py:191+` | no. signature omits `gt`/`lt`/`eq`/`multiple_of`/`in_choice` (only `**kwargs`) |
| Email pattern | `EmailIDValidator` | `:2169` | no. pattern=`relib.email_pattern` |
| Payment card brand + Luhn | `PaymentCardValidator` | `:2194`, `paymentcards.py:110` | **#3**, **#4** |
| Phone (`phonenumbers`, default region IN) | `PhoneNumberValidator` | `:2230` | **#4** |
| Path exists | `PathValidator` | `:2268` | **#4**. not LOCKED |
| IPv4 / IPv6 / any | `IP*AddressValidator` | `:2311-2356` | **#4** |
| Aadhaar Verhoeff | `AadhaarCardValidator` | `:2360` | **#4** |
| PAN regex findall | `PANCardValidator` | `:2392`, `pancard.py` | **#4**. `verify`/`generate` unused teaching |
| Mapping/Sequence/List/Dict/Set/Tuple/Enum/UUID | typed `*Validator` | `:2152-2445` | annotation only. not LOCKED |
| Schema v2 regex map on Field | `Schema` | `schemas_v2.py:21` | HOLD dual-schema. `blank=` (`:30`, `:52`) is not `required`. It falls into `Logger.kwargs` |
| Schema v1 `make_dataclass` | `SchemaValidator` | `schemas.py:34` | parked |
| Logger files | `Logger` | `loggers.py:29` | no |
| Pattern combinators | `Pattern` et al. | `regexps.py` | no |

## 5. Usage patterns

`examples/` is absent from `git ls-tree`. Callers live in README, docstrings, and tests.

**Door A. Validator as the dataclass default (dominant, LOCKED).**

```python
@dataclass
class User(object):
    name: str = StringValidator(logger=False, debug=True, max_length=50, required=True)
```

Cites. `README.md:37-45`. Re-locked `test_soft9_composable_bounds.py:104`, `test_soft10_validation_path.py:175`. Integer mix of min/max/`multiple_of` at `test_soft9_composable_bounds.py:124`.

**Door B. Field factory, then `.validator` as the dataclass default (CLAIMED, not LOCKED).**

```python
password_field = valio.StringField(min_length=6, max_length=30, debug=True, required=True)
...
password: str = password_field.validator
```

Cites. `README.md:66-128`. `Field.__init__` `fields.py:218`. The `Field` signature lists `min_value`/`max_value` but not `gt`/`lt`/`eq`/`multiple_of`/`in_choice`. Those only reach the validator via `**kwargs`. Schema v2 `__main__` repeats Door B (`schemas_v2.py:184-197`). Decorators hang on the Field (`@user_field.add_pre_valiator` typo at README `:79`; real `add_pre_validator` at `fields.py:128`). Zero Field tests.

**Inheritance vs composition.** Pre-Soft, `ValueValidator` dual-inherited min+max and `Validator` 11-way inherited every concern (`5a574a5` lines 728, 913, 1345). Soft #9 made Value/Length subclass `ValidateProperty` only (`validators.py:984`, `:1173`). Soft #10 did the same for `Validator` (`:1581`). Tests lock `issubclass(..., MinValueValidator) is False` (`test_soft9_composable_bounds.py:56-74`, `test_soft10_validation_path.py:84-105`). Typed aliases still subclass `Validator` (`:1971`, test `:89`).

**Property descriptors.** `test_descriptors.py` drives `Property` set/get/delete and the Soft #2 falsy-default lock (`:190-221`). `__get__` on the class returns `None` because `if obj is None: return` (`descriptors.py:278-279`).

**Path validation.** `PathValidator` (`validators.py:2268`) plus `PathField` (`fields.py:571`). No tests. `path_exists` is a kwarg. Existence check is `value.exists()` after `is_file() or is_dir()` (`:2303-2308`), which is redundant for real paths.

**Pattern composition.** README regex section (`:140-170`) builds dates with `Pattern &` / `|` and `WordBoundary`, then `pyparsing.Regex(...).re_match`. Product date/email/card helpers use the same combinators. PatternValidator itself takes a string or `PatternType` and runs `findall` (`validators.py:504`). Tests accept substring `"a string"` for `r'\w+'` (`test_validators.py` `TestPatternValidator`).

**Shared validator instance.** `test_type_class_validator` documents that one `TypeValidator` reused across classes fails when annotations are not a subclass (`test_validators.py:85-135`). That is LOCKED as a collision, currently ERROR vs expected `RuntimeError`.

**Processing then tasks.** `test_task_processing_order.py:28`. `add_pre_validator` mutates the value. `add_pre_validator_task` observes the mutated value once. Namespace must match the dataclass name (`namespace="Host"`). Get/delete processors receive the attribute name, not the stored value (`:76-77`).

## 6. A9 candidates

These are the composition units the library is actually made of. Not a new framework. Count is six.

1. **Descriptor lifecycle.** `Property` `__set_name__` / `__set__` / `__get__` / `__delete__` with debug-swallow. Everything else hangs off this.

2. **Concern leaf.** One class, one check (`TypeValidator`, `RequiredValidator`, …). Soft #9/#10 made facades call these instead of inheriting them.

3. **Bound presence.** `None` means unset. `0` means specified. `_all_specified` (`validators.py:619`) is the encoded rule. Inclusive min/max vs exclusive gt/lt live here.

4. **Validation path.** `_ValidationPath` (`:820`) is an ordered unique list of unit names. `value` owns `min_value`/`max_value`/`eq`. `length` owns `min_length`/`max_length`. Double-call and aggregate+leaf fail closed. A second `validate()` is a new pass (`test_soft10_validation_path.py:134`).

5. **Hook split.** Processors (`_processing`) return a possibly new value. Only the `pre_set` pipeline return is stored. Tasks (`_after_processing_run_tasks`) run once after, cache keyed by `id(tasks)`. Get/delete processors see `self.name`, not the stored value. Soft #7 exists because processing and tasks were the same MRO override.

6. **Pattern combinator.** `PatternType` `&` / `|` plus relib named patterns. This is how Email/Date/Card strings are built. pyparsing `Regex` is a matcher, not the combinator.

Field, Schema v2, and typed `*Validator` aliases are facades over 1-5. They are not extra units.

## 7. Pain map (what Softs papered over)

User rejected the Soft-patch stack as brittle, fragmented, and ugly. The holes below are why Softs existed. They are not a request for Soft #11.

**Dual doors.** Door A (Validator-as-field) is the tested product. Door B (Field factory + `.validator`) duplicates kwargs (`fields.py:194-240` vs `Validator.__init__` `:1670`) and omits `gt`/`lt`/`eq`/`multiple_of`/`in_choice` from the Field signature. Schema v2 is a third door on Field (`schemas_v2.py:21`). `blank=` is not `required`. It lands in `Logger.kwargs`. README teaches both doors and a typo decorator. ux-valio should pick one caller shape.

**Inheritance spaghetti.** Pre-Soft `Validator` already inherited eleven concern classes (`5a574a5:1345`). Softs did not invent that MRO. They papered over bugs it caused. Class bases did not move in P0/P1 #2-#6 or Soft #7/#8. Soft #9 changed only `ValueValidator` / `LengthValidator` to `(ValidateProperty)`. Soft #10 is the only SHA that changes `class Validator(...)`. Residue on tip is method-copy, not a new object graph (`Validator._validate_type = TypeValidator._validate_type` at `:1644`, copied task methods `:1660`). `StringValidator._validate_min_value` still special-cased (`:2012`). `_validate_field` still collects a results list from side-effecting calls. Path uniqueness is the new gate. Source-lock tests freeze helper names (`_validation_path`, `_all_specified`, `_enforce_min_bound`).

**Soft #8 honesty bugs (must not regress).**

Pre-Soft gates used truthiness. `if self.min_value is not None and self.min_value` (`5a574a5` MinValue `_validate_min_value`). Same for max/eq/length/`multiple_of`. Bound `0` was skipped.

`gt`/`lt` were stored as min/max (`self.min_value = min_value or gt` at `5a574a5` MinValue `__init__`) and checked inclusive (`value < min_value`). After Soft #8, `gt`/`lt` are exclusive (`>` / `<`), `min_value`/`max_value` inclusive (`>=` / `<=`).

`MultipleValidator` used inverted `value//self.multiple_of == 0` (`5a574a5` remainder block). That is true for any `|value| < |n|`. It also skipped `multiple_of=0`. After Soft #8, remainder is `value % n == 0`. `multiple_of=0` only accepts `0` (`validators.py:607-610`). `TestMultipleValidator.test_multiple_of_validator` in `test_validators.py` still does not lock `%`. The honesty file does.

RED lock. `valio/tests/validator/test_bound_honesty.py` (15 tests, all ok on this machine).

**Soft #7 `_processing` / `TaskValidator`.**

Pre-Soft `Validator` inherited `TaskValidator` and re-overrode every `*_processing` hook. `_processing` also called `_job` (`5a574a5:1521-1535`). Tasks lived in two places. `TaskValidator` hooks ran `_job` then discarded `super()`'s return (`5a574a5:1315-1318`). `_job` used `getattr(self.task, tasks)` on a defaultdict, which TypeErrors when `cache_task=True` (the default). Standalone `TaskValidator` stored `None` instead of the assigned value.

Fix (PR #7 `4c3d0dd`). `_processing` only runs processing funcs. Tasks run once after via `super()` into `TaskValidator` (Soft #10 rephrased as `_after_processing_run_tasks` without inherit). Cache keys are `id(tasks)` (`validators.py:1494`).

**Soft #9 `_all_specified`.**

Soft #8 made gates `is not None`, so mutual exclusion became noisy `A is not None and B is not None`. Soft #9 folded that into `_all_specified` (`validators.py:619`). Same meaning. `0` is present. `None` is unset. Never truthy `all([A, B])` (pre-Soft MinValue `__init__` used `if all([min_value, gt])`). Value/Length stopped dual-inheriting.

**Soft #10 `ValidateProperty` + `_ValidationPath`.**

Soft #9 only composed Value/Length. `Validator` was still 11-way inherit through Soft #9 (`git show 14d253e:valio/validator/validators.py` class `Validator(` still lists eleven bases). `_validate_field` built a side-effecting list of leaf calls. A second `min_value` next to `value` could double-call. `StringValidator._validate_min_value` copy-pasted inclusive/exclusive conditionals.

Soft #10 assembles units on `_ValidationPath`. Public kwargs KEEP. Soft #8/#9 KEEP.

**Earlier P0/P1 (not Soft-named, same honesty pass).**

| PR | SHA | Lie |
| --- | --- | --- |
| #2 E14 | `b2b17c65d7577bb4cd3af4fcbd205db8a8cca546` | `value or default` ate `0`/`False`/`""` |
| #3 E13 | `e8284b6110cd643bb830e33e141913f8e472f9c7` | `scanString` generator always truthy. any Luhn string passed |
| #4 E15 | `51f7df150fa3b18bb33f23a22390f3db4ef77b14` | named `validate()` called `add_validator` on every assign |
| #5 E16 | `eb4ce37121431fd425694d61c10a26bc486391ef` | one-sided bound compare TypeError. `DecimalValidator.value` was `DEBUG` |
| #6 E18 | `a647ad11005d92e4974c1909d18752a6c16e72ad` | `expire_before` pattern-checked `expire_after` |

**Still ugly on tip (not invented Softs).** HSL validator uses RGB patterns (`:2082`) plus `r_rbga` (the exported name is `r_rgba`). Soft #8 did not sweep leftover truthy gates on `required` (`:445`), `expiry` (`:1296`), `in_choice` / `not_in_choice` (`:1396`, `:1415`), `has_attributes` (`:1459`). Empty choice/attribute lists would skip. `enable_async` uses `asyncio.run` inside the setter. Logger default-on. Dual Field/Validator/Schema constructors. Star-import barrel. `Dust*` names. Unused `color_format.py`. Schema v1 parked beside v2. Pattern `findall` vs named-color `fullmatch`. Source-lock tests that grep helper identifiers. CHANGELOG Soft #10 says "Regex / rule / dual-schema untouched" with no `rule/` folder in any commit.

## 8. HOLD surfaces

Do not invent Softs for these. Report what is in tree vs parked.

**Dual-schema.** Both files exist from the initial commit `fd54782348aeb5529e082955b35f7b5b46f9912e`. `valio/schema/__init__.py:8-9` has commented `from .schemas import *` and live `from .schemas_v2 import *` in that same initial commit. v1 (`schemas.py`) is live unused source (286 lines), not a stub. Only the import is parked. v2 (`schemas_v2.py`) subclasses `fields.Field`, adds a regex map, and drops Positive/Negative/Email/Phone/PaymentCard schemas. `blank=` is not wired to `required`. No schema tests. HOLD means do not Soft-patch schema unification on valio. ux-valio may drop both or design one schema door from scratch.

**typingx.** In tree as a runtime dependency (`pyproject.toml:9`). Used. `from typingx import isinstancex` (`validators.py:65`, type check `:408`). `from typingx import issubclassx` (`descriptors.py:13`, annotation match `:174`). Not parked. HOLD means do not Soft-patch a new typing layer or drop the dep as a "cleanup" on valio. ux-valio may keep union-aware checks or replace them with stdlib, but must not silently change `Union` matching (the reused-validator test already collides).

**pyparsing.** In tree as a runtime dependency (`pyproject.toml:11`). Used in product relib, not only README. `from pyparsing import Regex` in `paymentcards.py:6` (`is_card_of_*` call `.re_match`). `import pyparsing as pp` in `emails.py:6` and `dates.py:9`. `regexps.py:494` imports it under `if __name__ == "__main__"`. README `:142` teaches it. HOLD means do not Soft-patch a parser rewrite. ux-valio may keep Pattern combinators and a matcher, or drop pyparsing if the matcher is stdlib `re`.

**Absent (do not invent).** `rule/` folder. Cap Host. `mount_channel`. `examples/`.

## 9. Test locks

Measured on tip after `pip install typingx phonenumbers pyparsing pytest toml`.

`python3 -m unittest discover -s valio/tests -t .` → 111 tests, 1 fail, 1 error (the two pre-existing ones). Soft #2-#10 files all ok.

`python3 -m pytest valio/regexer/tests/regex_test.py -q` → 3 passed, 1 failed (`test_preceded_by`).

| File | What it locks |
| --- | --- |
| `valio/tests/descriptor/test_descriptors.py` | Property set/get/delete, `__set_name__` docs, **Soft #2** `0`/`False`/`""` not replaced by default (`:190-221`) |
| `valio/tests/validator/test_validators.py` | version vs poetry, TypeValidator debug-swallow, Required, Pattern `findall`, Reassign. `TestMultipleValidator` does **not** lock remainder |
| `valio/tests/validator/test_payment_card.py` | **#3** Visa test number accepted. Luhn-valid non-brand rejected. Luhn-invalid rejected |
| `valio/tests/validator/test_named_validate_once.py` | **#4** HexColorValidator custom list does not grow across assigns |
| `valio/tests/validator/test_value_validator_init.py` | **#5** one-sided `value=` no TypeError. `eq=0` kept. value above max still raises |
| `valio/tests/validator/test_expiry_validator.py` | **#6** `expire_before` string sets timeline `before`. bad string rejected. `expire_after` only still sets timeline |
| `valio/tests/validator/test_task_processing_order.py` | **#7** processing then task once. all phases. processing without tasks. standalone TaskValidator keeps assigned value |
| `valio/tests/validator/test_bound_honesty.py` | **#8** see below |
| `valio/tests/validator/test_soft9_composable_bounds.py` | **#9** `_all_specified` None-only. compose-not-inherit. public ctor KEEP. `0` still conflicts on exclusive pairs. source grep locks |
| `valio/tests/validator/test_soft10_validation_path.py` | **#10** Validator does not inherit leaves. path fail-closed. public usage KEEP. bound honesty on the facade. source grep locks |
| `valio/regexer/tests/regex_test.py` | Pattern quantifiers, SetOf, preceded-by (currently FAIL vs special_chars set) |

### Soft #8 bound honesty (must not regress)

File `valio/tests/validator/test_bound_honesty.py`. 15 tests, all ok.

- **`is not None`.** `min_value=0` / `max_value=0` / `min_length=0` / `max_length=0` / `length=0` / `eq=0` / `value=0` / `multiple_of=0` are stored and enforced (`TestBoundHonestyZeroIsABound`, `TestBoundHonestyEqValueZero`, `TestBoundHonestyMultipleOf`).
- **Exclusive gt/lt.** `gt=0` rejects `0` accepts `1`. `lt=0` rejects `0` accepts `-1` (`TestBoundHonestyExclusiveGtLt`).
- **Inclusive min/max.** `min_value=0` accepts `0` rejects `-1`. `max_value=0` accepts `0` rejects `1`.
- **Length 0.** exact `length=0` accepts `""` rejects `"x"`. `max_length=0` same. `min_length=0` accepts `""` and `"x"`.
- **Multiple `%`.** `multiple_of=2` accepts 0/2/4, rejects 1/3. `multiple_of=0` accepts `0`, rejects `1`, no `ZeroDivisionError`.

Soft #9/#10 re-lock the same facts on facades (`test_soft9_composable_bounds.py:157-184`, `test_soft10_validation_path.py:231-260`). `Validator(min_value=0, gt=0)` still conflicts because `_all_specified(0, 0)` is true.

## 10. Migration notes (L-monotonic vs Soft residue)

**Preserve (behavior tests lock, or README happy path the Softs promised to KEEP).**

- Descriptor-on-dataclass assignment. Callers write a field default that validates on set.
- `debug=True` raises. `debug` falsy swallows and readback is `None`. Do not flip the default to fail-closed without an explicit ux-valio product decision. PLAN K1 called this locked.
- Falsy assigned values (`0`, `False`, `""`) are not replaced by `default`. `None` is.
- Bound presence is None-only. `0` is a bound.
- `gt`/`lt` exclusive. `min_value`/`max_value` inclusive. `eq`/`value` equality.
- Length has no exclusive aliases. Length `0` works.
- Multiple-of is remainder. `multiple_of=0` only accepts `0`.
- Named payment cards match a brand, not "any Luhn generator".
- Named validators do not register themselves on every assign.
- One-sided bound construction does not TypeError.
- `expire_before` pattern-checks itself.
- Processors run before tasks. Tasks run once per phase. Assigned value is kept.
- Public constructor names and kwargs used in README (`StringValidator`, `max_length`, `required`, `in_choice`, `min_length`).
- Pattern substring `findall` if ux-valio keeps PatternValidator semantics (PLAN K4). Changing to `fullmatch` is a product break. Named hex colors already use `fullmatch`.
- `phonenumbers` behavior for `PhoneNumberValidator` if that name is kept.

**Retire as Soft residue (do not port the patch shape).**

- 11-way MRO and the alias-method compose that replaced it. ux-valio should have one composition story, not inherit-then-uninherit.
- `_all_specified` / `_ValidationPath` / `_enforce_min_bound` as public-ish helpers that tests grep by identifier. Port the behaviors, not the helper names, unless you want those tests.
- Dual Field vs Validator constructors that copy kwargs. Field omits `gt`/`lt`/`eq`/`multiple_of`/`in_choice` from the signature. Pick one door.
- Schema v1 parked next to Schema v2. `blank=` is not `required`. Pick one or none.
- Leftover truthy gates on choice/expiry/attributes. Soft #8 was numeric/length/`multiple_of` only. Do not treat empty-list skip as bound honesty.
- Method-copy compose (`_validate_* = Leaf._validate_*`) and the leftover `_validate_field` results list. Port path uniqueness behavior, not the alias table.
- `Dust*`, unused `color_format.py`, unused `profile` / `timed_lru_cache`, PAN `generate`/`verify` teaching, schema `__main__` password demos.
- `Validator.register` cargo-cult. `add_pre_valiator` typo. Do not add aliases.
- Star-import barrel as the public API. Export an explicit `__all__` in ux-valio.
- `asyncio.run` inside `__set__` as "async validation". If ux-valio wants async, design it. Do not copy this.
- Source-lock tests that freeze Soft architecture (`class Validator(ValidateProperty)` AST, "must not contain `all([min_value, max_value])`"). Those tests exist to stop valio from regressing into the old MRO. A new repo does not need them once composition is the only path.
- HSL-using-RGB and `r_rbga` typo. Do not port the bug.

**L-monotonic rule for the new repo.** Any ux-valio release that claims a named capability (bounds, payment card, reassign-once, debug swallow) must keep the LOCKED facts above. Capabilities that are only CLAIMED or EXPORTED (Schema, Field door, async, Path, Aadhaar, dynamic docs) may be redesigned or dropped. Do not silently change a LOCKED fact to make the architecture prettier.

Soft LOCK. No more Soft patches on valio. This file is the source map for `ux-valio`.
