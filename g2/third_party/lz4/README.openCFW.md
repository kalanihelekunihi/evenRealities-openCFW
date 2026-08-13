# LZ4 v1.10.0 authenticated upstream snapshot

This directory contains byte-for-byte source from the official
[`lz4/lz4` `v1.10.0`](https://github.com/lz4/lz4/tree/v1.10.0) tag at
commit
[`ebb370ca83af193212df4dcbadcc5d87bc0de2f0`](https://github.com/lz4/lz4/commit/ebb370ca83af193212df4dcbadcc5d87bc0de2f0).
The snapshot is limited to the block codec source, public header, and complete
BSD-2-Clause library license.

The snapshot is an authenticated source candidate, not proof of the original
G2 checkout. Primary upstream inspection corrected an earlier recovery claim:
official `v1.9.4` already contains the three-argument variable-length reader,
strict `*ip > ilimit` bound, `rvl_error` sentinel, and 32-bit accumulator
guard. The stripped G2 code therefore does not currently distinguish `v1.9.4`
from `v1.10.0` on those markers.

The isolated adapter at
`research/candidates/evenhub_lz4_1_10_0.c` preserves the existing G2-facing
`open_cfw_lz4_decompress_safe` ABI and delegates directly to pristine upstream
`LZ4_decompress_safe`. It is not listed by a production overlay or manifest.
Production still compiles the existing hand-bounded decoder until a separate
promotion updates attribution, build inputs, target relocation handling, and
all aggregate artifact pins atomically.

Verify the upstream byte identities, version markers, isolation boundary, and
official firmware spans without network access:

```sh
python3 openCFW/third_party/lz4/verify_snapshot.py
```

The verifier is read-only. The candidate implements only the independent,
no-dictionary safe-decompression call used by EvenHub. No compressor API is
needed by the candidate.
