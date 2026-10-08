# Resource/dependency shortcut

`dependency-map.json` records the reusable source and licensing boundaries. LVGL core pin `344c7c318047b7348e1be8572a9fd4260c251cfa` is a hybrid 9.3-development baseline; the separately documented Ambiq draw backend has exact subtree tree `1e774257495fa43177e04fc5c8a42a77c2d7d619`. `libraries.md` documents the backend and Nema headers under `g2/third_party/`, but those paths are absent in this checkout. The docs also record liblc3 v1.1.3 pin `96a3af0beb5487aca3b98a4b992a539a1f6d80d1` and provenance path `g2/third_party/liblc3/PROVENANCE.json`; that path is also absent here. This is a checkout availability statement, not a claim that the source never existed. Proprietary Nema implementation source remains unavailable; headers explain interfaces and public GCC archives differ from stock IAR objects.

`candidate_descriptor.py` verifies one authentic, previously unresolved image candidate in the official payload: descriptor runtime `0x7682b0` (payload `[3343056,3343084)`), with 55×48 pixels at `[2373520,2376160)`. Its descriptor and pixel bytes hash-match the existing candidate inventory. The inventory records one pointer occurrence at payload offset `0x187944` (`0x5bf924` under the established runtime mapping), but does not establish a constructor/direct-call/consumer chain. The checker records this as bounded structured data and leaves it unresolved; it does not increase coverage. Tests include positive authenticated bytes and wrong-layout, wrong-extent, wrong-address and wrong-payload controls.

`resource_metadata.py` continues to authenticate the six prior mapped L8 ranges and export metadata only. Those 28,872 bytes are not new classification. Neither tool extrapolates a format from examples or recreates external NOR content.

Run the local tests with:

```sh
python3 -m unittest discover -s g2/analysis/rescan-2026-10-07/implemented/resources -p 'test_*.py'
```

Remaining evidence needed to promote `0x7682b0`: disassemble and validate the code at/around the pointer occurrence (`0x5bf924`), prove a literal load and direct call or another reliable consumer relation to `0x7682b0`, then bind that consumer to the established decoder admission/geometry checks. No original-instruction execution was undertaken here.

## Recovered-input validation

`verify_reference_inputs.py --output receipt.json` checks all91 recovered reference files against sizes, SHA-256 and historical Git blob identities. `reference-input-validation.json` passes; `reference-negative-controls.json` records wrong-identity and missing-file rejection. Dependency-map paths now point to recovered snapshots. This does not classify additional firmware resources or establish stock compatibility.
