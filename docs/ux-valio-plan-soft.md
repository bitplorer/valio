# Soft PLAN — greenfield `ux-valio` (NOT Soft-patches on valio)

**Soft LOCK.** Soft DO = **plan only** until TELOS/CTO/PR Reviewer Council issues **CLEAR**. Soft-patch path on `bitplorer/valio` KEEP **parked** at tip `3415c03e37085adda4040671a91eb19aa4fe4ac4` (Soft 10 merge). No empty-repo Soft, no product code, no Soft #11 on valio.

**Authoritative inputs.** Evidence Pack = `docs/ux-valio-source-map.md` (this PR). Standards brief informs only — do not invent A9 beyond pack §6 six disk primitives unless MAP/DEFER.

**Tip.** `origin/main` = `3415c03`. Pre-Soft baseline `5a574a5`.

## 1. Intent Lock
Descriptor on dataclass field; `Property.__set__` (`descriptors.py:253`) default-if-None (`:262`) → pre_set → store → post_set. `ValidateProperty.pre_set` (`validators.py:182`). Progressive validation with dataclasses — not Pydantic, not schema DSL, not fail-closed-by-default parser.

## 2. Framework Lock
Descriptor-native compose of concern leaves + ordered path. No Clean Arch. No Pydantic. No 11-way MI. Result type DEFER.

## 3. A9 (pack six)
1. Descriptor lifecycle — `descriptors.py:253-329`
2. Concern leaf — e.g. `TypeValidator` `:359`
3. Bound presence — `_all_specified` `:619`; Soft #8 honesty
4. Validation path — `_ValidationPath` `:820`; Soft #10
5. Hook split — processors vs tasks; Soft #7
6. Pattern combinator — `regexps.py` `&`/`|`
Standards check→#2, map→#5, all→#4; any/not/optional DRAFT MAP; each/mapping/schema DEFER.

## 4. Surface Lock
Door A (Validator as field default) KEEP. Door B (Field→.validator) RETIRE. Schema v1/v2 RETIRE from install unless later CLEAR. Explicit `__all__` (no 306 star leak).

## 5. L preserve vs RETIRE
KEEP Soft #2–#10 honesty behaviors (falsy defaults, brand cards, named-once, one-sided bounds, expire_before, task order, bound honesty, compose-not-inherit, path fail-closed). RETIRE MI/method-copy, dual Field door, Schema mess, truthy leftovers, RGB/HSL crash (`r_rbga`), Dust*, asyncio.run-in-setter as product, Soft source-grep architecture tests.

## 6. Migration
Door A almost same. Door B named migration to Door A. Schema named drop/redesign. Star-import break with leftover teaching.

## 7. Production nuts
py.typed; Hypothesis on honesty facts; no eval/pickle/exec. **PRODUCT DECISION:** fail-closed vs debug-swallow (LOCKED swallow today `descriptors.py:269-274`) — do not flip silently. Logger default-off. typingx/pyparsing HOLD decisions for greenfield.

## 8. Soft DO / NOT after CLEAR
DO: empty-repo Soft ux-valio; behavior tests for Soft #2–#10; one composition story; migration guide; freeze valio@3415c03.
NOT: Soft-patch valio; Soft #11; invent rule/Cap/mount_channel; invent A9; dual doors forever; silent fail-closed flip.

## 9. Dual-door valio/ux-valio
RETIRE Soft-patch path. KEEP valio@3415c03 frozen reference. Greenfield ux-valio = progressive-validation product.

## STOP
Council CLEAR then human proceed before empty-repo Soft. Soft DO now = Council review only.
