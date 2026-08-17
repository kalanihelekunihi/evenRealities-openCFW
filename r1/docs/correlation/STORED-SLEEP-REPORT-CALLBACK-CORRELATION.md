# R1 stored-sleep report callback correlation

Status: 118-byte callback byte-pinned; bounded pure dispatch planner implemented.

The curated Ghidra sleep evidence names `0x0008F954`, but the exported function inventory folded
that independent body into a distant noncontiguous range. The Thumb body has its own prologue and
return boundary at `0x0008F954..<0x0008F9CA`. Its exact SHA-256 is
`32061a5ba2b5791a49e9f0590a8c4b41dcc597f4494ef2264374be6c71ad3edb`. It has no direct branch
callers because the request wrapper at `0x0008B818` loads its Thumb pointer `0x0008F955` from
`0x0008B830` and passes it to the stored-sleep iterator at `0x0005B39C`.

The iterator invokes the callback with a validated record descriptor, a 32-byte sleep header, the
compact record length, and a private three-byte context. Context byte 0 is the report type; the
little-endian UInt16 at offset 2 is the stage count. A null context returns false. Synchronization
flag `1` returns true without sending. Every other flag forwards the header, context fields, and
record descriptor to the compact-to-phone packet builder at `0x0008DA24`, then returns true. The
packet builder supplies public model identifier `0x0601`.

`r1_sleep_sync_plan_report_callback` in `src/r1_storage.c` implements only that decision policy.
It returns a typed intent containing the callback result, synchronized-record skip, packet-builder
request, report type, stage count, and model identifier. It performs no pointer dereference,
logging, allocation, flash access, marker mutation, packet construction, callback registration, or
BLE send. Existing bounded packet construction and acknowledgement planning remain separate.

Tests cover a null output, missing callback context, exact synchronization flag `1`, ordinary
dispatch, preservation of the full UInt8/UInt16 context fields, and the stock distinction between
flag `1` and other nonzero values.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_sleep_sync.py
make test
```
