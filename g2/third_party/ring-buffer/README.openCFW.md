# AndersKaloer/Ring-Buffer compatibility snapshot

This directory selects official upstream commit
`190e30bebcec22d7311fd941179d70b4f439c441` as openCFW's reproducible
compatibility source. It is the newest source-equivalent commit available
before the G2 firmware build timestamp (`2025-04-28T13:29:15Z`). It is not a
claim that Even Realities used that exact checkout.

The official binary proves the compatible interval
`cda00e1efb815bad5100757f0d10d117f633ced6` through `190e30b...`:
`cda00e1` introduced the observed dynamic 16-byte object, runtime power-of-two
assertion, and buffer-size parameter. The complete seven-function stock
cluster preserves the same API, overwrite-oldest policy, and control flow.

`ringbuffer.h` is byte-exact. `ringbuffer.c` drops one redundant terminal blank
line, and `LICENSE` adds a terminal LF. The offline verifier reverses those two
documented normalizations before checking the official Git blob IDs.

The seven-function stock closure is production-integrated through the bounded
adapter at `components/shared/ring_buffer/runtime_ring_buffer.c`. The reviewed
Apple-Clang build contributes 248 source-owned bytes plus four alignment bytes;
all 252 callable stock-span bytes (250 instructions plus two alignment bytes)
are entry-redirected. The Linux-Clang aggregate
remains pending and is not inferred from the Apple build. Run:

```sh
python3 third_party/ring-buffer/verify_snapshot.py
python3 tools/analyze_g2_ring_buffer.py --json
python3 -m unittest tests.test_ring_buffer_snapshot
```

See `docs/research/ring-buffer-lineage-recovery-audit.md` for the binary proof,
production layout, and remaining cross-toolchain replay work.
