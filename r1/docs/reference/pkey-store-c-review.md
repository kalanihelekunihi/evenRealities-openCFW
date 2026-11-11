# R1 pKey flash-store C provider

`r1/src/application/runtime/native_health_key_store.c` supplies canonical
`r1_health_pkey_store_native` and its existing event-service alias
`r1_event_service_0006b724`. This closes the missing hardware persistence
provider called by event callback 0x42b20. It reuses the shared FAL owner,
existing binder, native allocator, memcpy and CRC implementation.

REA has no defined procedure at 0x6b724. The caller tail branch and instructions
were inspected directly; fresh REA byte evidence covers 836 bytes from 0x6b724,
including the routine and nearby literals/strings, and matches the preserved
application image. The evidence ID, hashes and build receipts are recorded in
[pkey-store-c-review.json](pkey-store-c-review.json). No decompiler agreement is
claimed.

The void entry accepts only a 64-byte key. It binds storage before the null-key
check, copies the key before calculating CRC, and probes eight bytes at the
partition offset **plus four**. If the first probe word is not erased, it erases
4096 bytes. It then writes the eight-byte length/CRC header at the partition
base and the copied key at base plus eight, frees the copy and logs success.
Shared partition/device pointers and callbacks are reloaded between operations,
including after callbacks which may change the shared owner. A partial read
preserves the initially saved length word for the erase decision. The second
scratch word is overwritten before use.

Observed device statuses are ignored, including failed erase/write operations;
the success log still occurs. This preserves the stock contract rather than
inventing error recovery. The allocation-null guard is preserved and tested,
but ordinary exhaustion of the existing native heap remains fatal. This entry
does not invalidate the separate cached authentication key.

The paired stock/C probe passes **1008 cases, 2064 executions**: 2016 store
executions and 48 load executions. It covers invalid lengths, null/unbound
storage, partial reads, status errors, logging modes, owner/key mutation by
callbacks and the actual event callback entry. Existing binding, memcpy and CRC
execute, and the resulting header is checked against an independent CRC oracle.
Twenty-eight cases execute the actual native heap with modeled scheduler
boundaries. Other cases use a modeled allocator, including the null guard.
Twenty-four write/load round trips execute the existing load routines, checking
valid persistence and rejecting corrupted lengths, payloads and failed writes.
All six compiled defect controls are detected: incorrect probe offset, inverted
erase condition, incorrect CRC, short payload, missing free and stale partition.

The fresh normal build compiles **800 units (718 application, 82 bootloader)**
without compile failures or duplicate strong symbols. Application imports fall
from 97 to **96**, with only `r1_event_service_0006b724` removed and none added.
All 797 nongenerated prior object hashes are unchanged. The two generated boot
objects have changed debug metadata but identical allocated bytes/relocations.
Strict GNU bootloader linking passes. R1 manifest checks pass; the global check
still reports the unrelated unlisted G2 `resident_rom_thumb_set.S` file.
No source-plan qualification is claimed or changed.

Flash lookup, callbacks and logs are modeled synchronously; the byte-array flash
model does not establish NOR programming physics or asynchronous behavior.
Private stack contents, incidental void-entry register outputs, faults and
concurrency are excluded. Physical flash/authentication behavior and a complete
application final link remain unverified. These results establish C compilation
and the scoped behavioral comparisons, not complete firmware readiness.
