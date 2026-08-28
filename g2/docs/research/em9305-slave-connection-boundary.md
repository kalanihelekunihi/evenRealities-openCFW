# EM9305 slave-connection typed boundary

Status: software-only, fail-closed candidate; not production-routed

Candidate license: MIT

Hardware validation: blocked by unavailable physical evidence

## Result

The largest remaining EM9305 residual, `[0x00329888,0x0032A4BE)` (3,126
bytes), now has an isolated typed provider boundary. This changes its readiness
decision from `unavailable_proprietary_controller_code` to
`typed_unsupported_external_boundary` without changing its provenance,
claiming source availability, or enabling production.

The existing authenticated cluster recovery proves six entry identities and
four two-byte `nop_s` paddings that exactly tile the segment:

| Entry | Stock range | Bytes | Evidence status |
|---|---|---:|---|
| `lctrSlvConnEndOp` | `[0x00329888,0x00329FD6)` | 1,870 | vendor-modified, 569/588 opcode alignment |
| `lctrSlvConnExecute` | `[0x00329FD8,0x00329FFE)` | 38 | exact size and 13/13 opcode sequence |
| `lctrSlvConnExecuteSm` | `[0x0032A000,0x0032A216)` | 534 | vendor-modified, 165/187 opcode alignment |
| `lctrSlvConnResetHandler` | `[0x0032A218,0x0032A22E)` | 22 | exact size and 7/7 opcode sequence |
| `lctrSlvConnRxCompletion` | `[0x0032A230,0x0032A47C)` | 588 | vendor-modified, 180/185 opcode alignment |
| `lctrSlvConnTxCompletion` | `[0x0032A47C,0x0032A4BE)` | 66 | vendor-divergent, 11/14 opcode alignment |

The eight padding bytes occur at `0x00329FD6`, `0x00329FFE`, `0x0032A216`,
and `0x0032A22E`. The whole stock segment SHA-256 is
`45c3d2477869a9ace185078ca6b5f59621eeca07ae274414e64637e5b04f12aa`.

## Boundary contract

The MIT source lives in:

- `components/shared/em9305/runtime_controller_slave_connection_boundary.c`
- `components/shared/em9305/runtime_controller_slave_connection_boundary.h`

It defines six stable OpenCFW entry IDs and an eight-word opaque invocation
carrier. Missing providers return `OPEN_CFW_EM9305_SLV_CONN_UNSUPPORTED`;
invalid IDs or carriers are rejected; provider failures are normalized to a
distinct status. The adapter forwards no call unless the caller supplies an
explicit reviewed provider.

The carrier is deliberately not represented as a recovered ARC prototype.
Arguments, return conventions, connection-context ownership, encryption and
retransmission state, channel-map transitions, scheduler interaction, and ISR
constraints are not complete. Inventing a C signature for those semantics
would make the boundary less safe, not more complete.

## License and source status

The candidate adapter is original MIT clean-room work. The function identities
come from a pinned Packetcraft/EM archive comparator with no repository-level
redistribution authority. Two bodies have exact size/opcode sequences only;
relocation-masked byte identity has not been established. Three are materially
vendor-modified and one is divergent. None is admitted as source, and no vendor
archive byte is copied into the adapter.

The earlier `em9305-controller-cluster-recovery.md` conclusion that the stock
bytes remain proprietary retention is still correct. This wave adds a typed
integration boundary on top of that provenance decision; it does not relicense
or replace the retained implementation.

## Readiness delta

| Readiness state | Before | After | Delta |
|---|---:|---:|---:|
| Typed external | 22 spans / 1,854 bytes | 23 spans / 4,980 bytes | +1 / +3,126 |
| Proprietary unavailable | 130 spans / 30,564 bytes | 129 spans / 27,438 bytes | -1 / -3,126 |
| Concrete source | 23 spans / 1,240 bytes | unchanged | 0 |

All 3,126 bytes remain release-blocking, so the total blocking census remains
152 spans / 32,418 bytes. The improvement is that callers now have a named,
machine-checked fail-closed seam instead of an undifferentiated unavailable
cluster.

## Reproduction

```sh
python3 tools/analyze_em9305_slave_connection_boundary.py --json
python3 -m unittest -v tests.test_em9305_slave_connection_boundary
python3 -m unittest -v tests.test_em9305_source_readiness
```

The focused tests compile the adapter freestanding with warnings as errors,
require zero undefined runtime imports, exercise every ID and failure path,
verify the evidence descriptors, mutate the parent cluster identity to prove
the analyzer fails closed, and check the exhaustive readiness delta.

## Remaining blockers

1. Obtain attributable, redistribution-compatible exact source or independently
   reconstruct the six complete state-machine behaviors.
2. Prove ARC arguments, returns, register preservation, interior callers,
   connection-context layout, ISR/thread context, and scheduler interaction.
3. Complete link placement and all direct/callback registration edges before
   considering production routing.
4. Future connection timing, encryption, retransmission, channel-map, and
   concurrency tests remain physical acceptance gates when authorized. They
   are currently blocked by unavailable physical evidence.
