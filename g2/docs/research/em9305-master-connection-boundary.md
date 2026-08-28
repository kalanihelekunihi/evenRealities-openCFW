# EM9305 master-connection typed boundary

Status: software-only, fail-closed candidate; not production-routed

Candidate license: MIT

Hardware validation: blocked by unavailable physical evidence

## Result

The third-largest remaining proprietary-unavailable residual,
`[0x0031DFD0,0x0031E5EC)` (1,564 bytes), is now an exact three-entry typed
boundary. Authenticated prologues, external call/branch references, returns,
and raw-body hashes establish this complete tiling:

| Address-derived entry | Range | Bytes |
|---|---|---:|
| `mst_conn_entry_31dfd0` | `[0x0031DFD0,0x0031E458)` | 1,160 |
| `mst_conn_entry_31e458` | `[0x0031E458,0x0031E4A0)` | 72 |
| `mst_conn_entry_31e4a0` | `[0x0031E4A0,0x0031E5EC)` | 332 |

Archive sizes and neighboring exact anchors correlate these bodies with
`lctrMstConnEndOp`, `lctrMstConnExecute`, and `lctrMstConnExecuteSm`,
respectively. Those names remain probable correlations, not exact source
admissions: matching archive disassemblies and redistribution authority are
not available. The enforceable adapter therefore uses address-derived IDs.

The original MIT boundary forwards an eight-word opaque carrier only to an
explicit provider and returns distinct invalid, unsupported, and failed
statuses. It contains no vendor implementation and claims no recovered ARC
prototype.

## Readiness delta

This wave moves one span / 1,564 bytes from proprietary-unavailable readiness
to typed external readiness. Current totals are:

- concrete source: 23 spans / 1,240 bytes;
- typed external: 25 spans / 8,348 bytes;
- proprietary unavailable: 127 spans / 24,070 bytes.

The release blocker remains 152 spans / 32,418 bytes. Production is still
blocked on attributable exact source or independent semantics, ARC ABI and
state ownership, complete scheduler/encryption/retransmission behavior,
placement, callers, and redistribution authority.

```sh
python3 tools/analyze_em9305_master_connection_boundary.py --json
python3 -m unittest -v tests.test_em9305_master_connection_boundary
python3 -m unittest -v tests.test_em9305_source_readiness
```

Future master-connection timing, scheduler, encryption, and concurrency
qualification remains an acceptance gate when authorized. Hardware testing is
currently blocked by unavailable physical evidence.
