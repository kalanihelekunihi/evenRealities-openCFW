# DaveGamble/cJSON v1.7.12 compatibility snapshot

This directory contains an authenticated, pristine cJSON snapshot from the
official lightweight tag `v1.7.12`, resolving to commit
`3c8935676a97c7c97bf006db8312875b4f292f6c` and tree
`6c770a14e7d9ac1a8fd452a32c51fa4462cf2b45`.

## Qualification

Version v1.7.12 is a deliberate openCFW compatibility choice at the ceiling of
the binary-proven interval **v1.7.9–v1.7.12**. Four independent binary
discriminators bound that interval (the ≥1.7.9 issue-#315 `get_object_item`
fix, the <1.7.13 `buffer_skip_whitespace` offset behavior, the absent <1.7.14
`parse_array`/`parse_object` `head->prev` tail store, and the <1.7.19 64-byte
stack `parse_number` buffer). All 21 linked parse-side functions are
byte-identical C text between v1.7.9 and v1.7.12 — re-verified
function-for-function during snapshot admission — so the stock image cannot
distinguish tags inside the interval. The whole-file diff between those tags
is confined to the print/create/edit/utils side, which static linking
dead-strips from the G2 image.

This snapshot therefore does **not** claim that Even Realities used the
v1.7.12 tag, this exact Git checkout, or any particular vendoring path. No
Even modification of the linked functions was found: the body is consistent
with an unmodified upstream cJSON built with `ENABLE_LOCALES=Off` (constant
`get_decimal_point`) and the default `CJSON_NESTING_LIMIT` of 1000. See
`docs/research/g2-json-parser-source-candidate-audit.md` for the complete
evidence.

## Included closure

The three pristine upstream files cover the linked parse-side closure:

- `cJSON.c`
- `cJSON.h`
- `LICENSE`, containing the complete MIT license text

`PROVENANCE.json` records the selected ref, commit, tree, parent commits,
compatible interval, file pins, and Git blob identities so
`verify_snapshot.py` can authenticate the snapshot offline without network
access or trust in a working-tree checkout.

## Recovered G2 link contract

The stock image links exactly 21 cJSON functions / 2,572 body bytes in the
physical interval `[0x004D798C,0x004D83D8)` (2,636 bytes including 64 noncode
bytes in six interleaved literal-pool/alignment gaps). All 34 external caller
sites terminate at six public entries and originate only from the two
already-closed sibling objects `service_android_notify.c` (13 sites) and
`service_whitelist.c` (21 sites). The six indirect `blx` sites are the cJSON
`internal_hooks` allocate/deallocate dispatches. Provider edges terminate at
the admitted nanopb 0.4.9 structure initializer, bounded IAR DLIB primitives
(`memset`, `strlen`, `strncmp`, `strcmp`), and two semantically bounded IAR
runtime bodies (`tolower` trampoline, `strtod`) owned by other frontier work.
No CMSIS-FreeRTOS or FreeRTOS kernel API is used.

## Production boundary

**Explicit decision: production-excluded.** The pristine translation units in
this subtree are authenticated reference material and are not linked. The
2,572 stock body bytes remain cut-forward in every build profile. Production
admission requires, at minimum:

- a compiler/ABI readiness matrix against this authenticated baseline,
- host-tested behavior verification of the candidate build,
- reviewed production-overlay integration with entry redirects,
- source-coverage and ownership accounting updates, and
- fail-closed tests pinning the resulting overlay, component, and package.

Identification and vendoring are not admission. Do not compile this subtree
into any production component without that review; `verify_snapshot.py`
fails closed if the recorded production-exclusion decision is removed.

## Verification

```sh
python3 third_party/cJSON/verify_snapshot.py
python3 -m unittest -v tests.test_cjson_snapshot
```

## License

cJSON is distributed under the MIT license. The complete unchanged upstream
text is retained in `LICENSE`; upstream source and header retain their
copyright notices.
