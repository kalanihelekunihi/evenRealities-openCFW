# EM9305 master periodic-scan / PAwR typed boundary

Status: software-only, fail-closed candidate; not production-routed

Candidate license: MIT

Hardware validation: blocked by unavailable physical evidence

## Result

The second-largest remaining EM9305 residual,
`[0x00321C30,0x0032233C)` (1,804 bytes), now has an isolated typed provider
boundary. Four authenticated entry bodies plus the exact two-byte `nop_s` at
`0x00322182` tile the segment with no remainder:

| Entry | Bytes | Evidence status |
|---|---:|---|
| `lctrMstPerScanRxPerAdvPktPostHandler` | 484 | vendor-divergent; 137/170 opcode alignment |
| `lctrMstPerScanTransferOpCommit` | 868 | vendor-modified; 267/283 opcode alignment |
| `lctrMstPerScanWithRspAbortOp` | 10 | exact size and 3/3 opcode sequence |
| `lctrMstPerScanWithRspCommitOp` | 440 | vendor-modified; 132/141 opcode alignment |

The whole segment SHA-256 is
`f1c6059c121b60e25cfcb722c6ee546af9d19acf06ab9b55d55bcde07eaae48d`.

The MIT adapter defines four OpenCFW entry IDs, an eight-word opaque carrier,
and distinct invalid, unsupported, and provider-failed statuses. It contains no
Packetcraft/EM implementation body, invokes nothing without an explicit
provider, and makes no claim that the carrier is the stock ARC ABI.

## Readiness and license effect

This wave changes one span / 1,804 bytes from proprietary-unavailable readiness
to a typed unsupported boundary. Across both controller-boundary waves, the
ledger now reports:

- typed external: 24 spans / 6,784 bytes;
- proprietary unavailable: 128 spans / 25,634 bytes;
- concrete source: 23 spans / 1,240 bytes.

The total release blocker remains 152 spans / 32,418 bytes. Function identities
come from the pinned Packetcraft/EM comparator, whose redistribution authority
is unresolved. One body is opcode-exact only, two are modified, and one is
divergent; none is source-admitted or relicensed.

## Reproduction and blockers

```sh
python3 tools/analyze_em9305_pawr_boundary.py --json
python3 -m unittest -v tests.test_em9305_pawr_boundary
python3 -m unittest -v tests.test_em9305_source_readiness
```

The suite compiles freestanding with warnings as errors, requires no undefined
runtime imports, exercises all entry IDs and failure paths, and mutates parent
cluster evidence to prove fail-closed behavior.

Production remains blocked on redistribution-compatible exact source or an
independent complete implementation, ARC ABI/state recovery, scheduler and
transfer semantics, callback placement, and all callers. Future PAwR timing,
scheduler, transfer, abort, and concurrency qualification remains an acceptance
gate when authorized; hardware testing is currently deferred by project
direction.
