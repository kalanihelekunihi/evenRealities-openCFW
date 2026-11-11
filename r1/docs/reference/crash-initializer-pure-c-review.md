# R1 retained crash-record initialization in ordinary C

The canonical initializer at `0x5a2b8` now uses C locals instead of its fixed-frame assembly adapter. Its private preparation helper is retired. The superseded, explicitly unlinked bridge file and its single manifest unit are removed, leaving one implementation. The retained-log caller now declares the checksum result correctly and explicitly ignores it; its compiled object remains identical.

The initializer captures the retained-record base, writes metadata and the low status bit, queries a private halfword length, and copies the opaque payload only for a nonnull pointer reporting 896 bytes. It then reloads snapshot inputs from the record, invokes the existing snapshot builder, computes the checksum over 964 bytes, and stores/returns it. The complete record extent is 966 bytes. Canonical cached-time and CRC declarations replace local incompatible types.

Validation passes 6,048 stock/C comparisons covering all 104 native instruction bytes, partial length writes, payload admission/copy boundaries, live snapshot fields and retained-base capture. Another 216 cases execute the actual offset/status access, payload getter, snapshot builder, cache accessors, hourly query, copy/CRC and state owners. Ten compiled defects are rejected.

The actual getter advertises 736 bytes, so it does not enter the separate 896-byte admission branch. The integration fixture verifies that the retained payload-copy region remains untouched in that case. The producer lifecycle remains unresolved; no 896-byte payload is fabricated or imported.

The final normal build compiles 862 units with 63 application imports and 22 bootloader imports. The count decreases only because the duplicate unit was already unlinked; participating object counts are unchanged. The tested initializer object matches the build. The other 851 prior nongenerated objects remain identical, including the caller and cached-status getter code. No persistent state is added, and source-plan selections are unchanged.

[The receipt](crash-initializer-pure-c-review.json) records hashes and proof boundaries. Direct clock/getter/snapshot boundaries are modeled; the full-chain fixture models only the backend timestamp and unreached logging. The separate snapshot builder still has its own assembly adapter. Private query-frame addresses and caller-scratch registers are excluded. Physical retention across reset, concurrency, final application linking and boot remain unverified.

The subsequent [snapshot builder conversion](crash-snapshot-builder-pure-c-review.md) removes the separate builder assembly adapter mentioned in this historical stage.
