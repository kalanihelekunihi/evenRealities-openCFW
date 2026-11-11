# R1 sleep sync report callback in C

The stock callback at application `0x8f954` now has a C implementation in
`r1/src/application/runtime/native_sleep_sync_report.c`, registered as one
unit in `r1/src/sources.json`. A null request returns zero. With a request,
source kind 1 returns one without logging or building a packet. Other kinds
log the report's first and last day, type and stage count according to the
live structured and SDK log modes, then pass the report, request kind and
count, and original source to the sleep sync packet builder.

The ignored probe at `build/r1-sleep-sync-report-probe-20261110/verify.py`
compares the locked stock function with the compiled C object in 144 paired
cases. It covers request presence, source kinds 0/1/2/255, nine log-mode
patterns, and provider changes to report and request fields. Call order,
formatted argument values, return value and observed buffers match. The
machine receipt is `build/r1-sleep-sync-report-probe-20261110/results.json`.

The strict R1 build compiles 884 application and 82 bootloader units with no
failures or duplicate strong symbols. The bootloader final link and vector
check pass. The strict application link still has 37 undefined references:
`r1_health_sync_provider_0008f954` is closed while the stock packet builder
at `0x8da24` becomes the new explicit import
`r1_sleep_sync_packet_builder`. Full flash load exceeds the configured
region by 28,984 bytes, 224 bytes above the prior checkpoint. Receipts are
under `build/r1-sleep-sync-report-c-20261110/`.

The lower logging and packet-builder providers were modeled in replay.
Actual packet construction, physical health transfer, complete application
linking, hardware execution and byte identity remain unverified.

The subsequent [packet and ACK chain](sleep-sync-packet-c-review.md) supplies
the lower packet builder, both module 6 event-post paths, and ACK callback
in C. The direct sleep sync callback and its lower chain now have no missing
imports of their own.

A first full `make sources` attempt was interrupted by a concurrent G2
codec source rename. The fresh rerun at
`build/sources-sleep-sync-report-stable-20261110/report.json` passed for
both device trees, with no compile failures or duplicate strong symbols.
`make sources-check` passes against the current manifests.
