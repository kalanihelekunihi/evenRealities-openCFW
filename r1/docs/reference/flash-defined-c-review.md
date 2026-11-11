# Defined C FlashDB read path and error propagation

The TSL and sector readers now use ordinary C with initialized scratch arrays.
Their assembly frame bridges are removed, along with the FlashDB read adapter
and FAL partition read register constraints. Successful reads retain the stock
status scanner, metadata order, record layout and diagnostics.

The adapter now requires an exact byte count. An incomplete or failed TSL read
returns error 2 without changing the caller's record. Failed sector reads mark
the sector invalid and return the error; nested TSL errors stop traversal.
Each of the iterator's three TSL call sites now branches to its existing unlock
and return path on failure. These are intentional improvements over decoding
stale stack data after a read error.

Verification passes:

- 3,549 successful stock/C comparisons through actual C sector, TSL, adapter
  and status bodies, with partition I/O and diagnostics modeled.
- 190 C-only cases for failed/short reads, different stack poison, nested read
  failures and file mode. Failed TSL records remain unchanged; failed sectors
  are invalidated and stop further reads.
- 9,216 FAL partition read regressions, including callback mutation, field order,
  diagnostics and public/private alias identity. Lookup/device services are modeled.
- Sixteen iterator error exits: four from normal entry and twelve controlled
  interior call-site entries. Every tested failure unlocks and avoids the user
  callback. Interior tests do not prove all normal iterator search routes.
- Four compiled defects restoring ignored TSL errors, short-read admission,
  ignored header errors and ignored iterator errors are rejected.

All 852 units compile and both relocatable payloads compose. All 839 other
nongenerated objects remain unchanged; the generated FAL unit changes as
expected. Imports remain 66 application and 22 bootloader symbols. R1 manifest
validation passes. No manifest or source qualification selection changes.

These checks do not establish physical flash behavior, final source linking,
startup or boot. An arbitrary provider that reports a full count after copying
partial data is not independently detected. Initialized buffers prevent
uninitialized C reads; they do not validate provider truthfulness. Private-stack
aliasing, arbitrary corruption and concurrency are outside the replay. Iterator
assembly and flash-write register constraints remain.

[Machine evidence](flash-defined-c-review.json) binds source, REA, probes,
negative controls and build reports. This supersedes the stale-frame requirement
in the earlier [flash frame review](flash-read-frame-review.md) for the changed
read paths; it does not claim equivalent failure behavior or byte identity.
