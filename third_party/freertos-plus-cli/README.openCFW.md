# FreeRTOS-Plus-CLI source snapshot

This directory contains the minimal official FreeRTOS+CLI V1.0.4 source and
license closure selected for openCFW. It is authenticated to FreeRTOS commit
`43defa566cc440251dbd6b48d1fcca27f88cfcdd` and tree
`1244875832c8ef8a39ee5b97a9dad657f7ea13ec`. The exact C/H blobs remain
unchanged at commit `1309654d6f5d1342b4a9d3d7ae0824e8fcaefaf2`.

This is an openCFW compatibility choice, not a claim that the G2 vendor used
either commit. The recovered machine code is compatible with the classic
V1.0.1--V1.0.4 lineage, while comments and dead-stripped configuration cannot
identify a unique historical checkout.

## Included boundary

The four official files are byte-for-byte Git blobs, including their original
CRLF line endings:

- `FreeRTOS_CLI.c` and `FreeRTOS_CLI.h`;
- `History.txt`, which declares V1.0.4; and
- `LICENSE_INFORMATION.txt`, the complete MIT component license.

`upstream/objects.json` stores base64 encodings of the exact selected and
file-pair-ceiling commit payloads plus the seven Git tree payloads required to
reconstruct both root tree IDs and prove path membership offline.
`verify_snapshot.py` recomputes all commit, tree, blob, SHA-256, license, ABI,
G2-span, patch, and production-exclusion pins without using the network.

## G2 delta

`g2-patches/0001-suppress-unknown-command-for-blank-input.patch` expresses
the one authenticated behavioral delta: for exactly carriage-return or empty
input, G2 does not copy the stock unknown-command message. The matching
instruction interval is `[0x005848CA,0x005848F4)`, 42 bytes, SHA-256
`4ed35ac83ff6802181aee553929f5eadff5e6b6c797601145d1c688c88eae7c1`.
The patch contains no Even command descriptor or handler.

## Deliberate exclusions

All 76 G2 command descriptors, command/help strings, handlers, and registration
order remain first-party glue. The console transport, firmware addresses,
production overlay registration, and hardware integration are also excluded.
Although the deployed path dynamically allocated 76 eight-byte list nodes, the
original `configSUPPORT_STATIC_ALLOCATION` state is not statically provable.
openCFW therefore leaves its eventual static-allocation policy unresolved
instead of presenting a guess as recovered configuration.

The effective G2 caller buffers are 128 bytes, and the safe NUL-terminated
input payload is 127 bytes. Those call-site facts do not recover
`configCOMMAND_INT_MAX_OUTPUT_SIZE` or
`configAPPLICATION_PROVIDES_cOutputBuffer`, because the upstream output
buffer accessor is absent from the retained G2 surface.

## Verification

```sh
cd openCFW
python3 third_party/freertos-plus-cli/verify_snapshot.py
python3 -m unittest -v tests.test_freertos_plus_cli_snapshot
```

This snapshot is production-excluded. The Makefile registers
`verify_snapshot.py` with the verifier-only `vendor-snapshots` dependency, but
neither the snapshot source nor its local patch is a compiler or linker input.
The verifier permits only that exact checking recipe and rejects references in
production manifests, component sources/build inputs, overlays, generated-patch
configuration, and firmware assembly tools.
