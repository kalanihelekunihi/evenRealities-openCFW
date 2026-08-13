# TinyFrame authenticated core snapshot

This directory contains byte-exact source from official
[`MightyPork/TinyFrame`](https://github.com/MightyPork/TinyFrame) commit
`eb75483e035916ef9f3e9fce0d2ae389cb09785f`. The selected commit first
introduced the exact `TinyFrame.c` and `TinyFrame.h` blobs selected by ten
retained G2 source-line diagnostics. Later repository head `a29167a` changes
only demo content and retains both core blobs, so this is an exact reusable
core-source pin rather than a claim about Even's historical checkout.

The upstream sources and examples are immutable MIT inputs. Recovered G2
configuration is isolated in `g2-config/TF_Config.h`. The official G2 build
also used short enums: with `-fshort-enums`, pristine `TinyFrame` is `0x7158`
bytes and its field offsets match the stock object after accounting for the
four-byte G2 prefix magic. G2 adds `0xA5A5A5A5` at the object head and
`0x5A5A5A5A` at `+0x715C`, producing a `0x7160`-byte vendor object. That magic
layout is not attributed to upstream and is not patched into this snapshot.

Likewise, `TF_Error`, `TF_WriteImpl`, listener callbacks, peer-role selection,
and the application transport remain explicit G2/first-party ports. Stock
analysis accounts for all 31 linked functions and the complete 3,118-byte
translation unit. The separate G2 adapter implements the
bookended allocation without modifying this directory and closes the
single-instance peer-role census. A second target-checked candidate binds the
adapter to source-owned `heap_4` and retains the authenticated first-party
synchronous write wrapper at `0x00541790`; the hardware provider behind that
wrapper remains stock. The stateless atomic boundary and inherited
`g2-production/TF_Config.h` are now production-routed as one eight-entry set.
They close the live 14-function dependency graph, select explicit no-op
logging, and reproduce exact complete overlays/components under both reviewed
Clang profiles. Hardware golden frames remain a validation gate, not a source
admission or provenance gap.

Offline verification:

```sh
python3 third_party/tinyframe/verify_snapshot.py
python3 tools/analyze_g2_tinyframe_send_version.py
python3 -m unittest tests.test_tinyframe_snapshot
python3 -m unittest tests.test_tinyframe_g2_production_ports_candidate
python3 -m unittest tests.test_tinyframe_g2_atomic_boundary_candidate
```

See
[`../../docs/research/tinyframe-send-version-recovery-audit.md`](../../docs/research/tinyframe-send-version-recovery-audit.md)
for the source-line, wire-format, object-layout, and transport evidence.
See also the
[`TinyFrame source-admission boundary audit`](../../docs/research/tinyframe-source-admission-boundary-audit.md)
for the separate G2 adapter and atomic-routing requirements.
