# Offline consume/empty and builder resets in C

Four consumers, four empty checks and four builder resets now have C providers. They reuse the source-owned offline rings/cursors introduced by [enqueue reconstruction](health-offline-enqueue-c-review.md); no second queue allocation is introduced. The [REA empty-check bytes](health-offline-consume-c-rea.json) match the locked application.

Consumers inspect the head timestamp and remove records while it is less than or equal to the cutoff. A future head stops the scan even if later entries could pass. Removed records are completely cleared, the read cursor advances modulo 24 or 144, and the byte count decrements; the write cursor stays unchanged. HR/SpO2/activity use four word stores per 16-byte entry. HRV clears twenty bytes and reloads cursor state afterward. Consumption is logged only when the consumed byte counter is nonzero, and remaining counts reload after log-mode/provider calls. Empty checks return exactly one for zero count and zero otherwise.

Builder resets preserve offset halfword, timestamp word and flag byte, clearing all other bytes. HR/SpO2 buffers are 148 bytes with metadata at +136, HRV is 220/+208 and activity is 1180/+1168. Null buffers return immediately. Existing notification-stage assembly now names these C providers directly: twelve symbol relocations replace eight unresolved legacy imports. Native callers reload R0 with the builder pointer after reset; the ignored incidental return value is not a C API requirement.

The [machine-readable receipt](health-offline-consume-c-review.json) records 2,576 stock/C comparisons for cutoff equality, future-head stopping, unsorted timestamps, wrapped/full queues, byte counts through 255, log-time state mutations, empty checks, unaligned builder buffers and metadata preservation. Mixed sequences execute actual C enqueue, consume and empty functions against the same storage.

A further 144 cases execute the actual stock flush callers at `0x4011c`, `0x442f4`, `0x4101c` and `0x3c578`, taking future-record rejection paths and tail-calling the actual C builder resets. Only clock/logging providers are modeled. Packet allocation/send and other flush branches are not established by these caller cases.

Six separately compiled defects fail runtime assertions: incorrect cutoff equality, activity capacity, incomplete record clearing, changing the write cursor, wrong builder metadata offset and lost flag restoration. The normal build compiles/composes 666 application and 74 bootloader units with no failures or duplicate strong symbols; `make sources-check` passes. Application imports decrease from 155 to 147 with no new imports; bootloader imports remain 34.

All 738 other prior objects are identical. The changed notification-stage object has identical allocated instruction/data bytes and identical relocations after normalizing exactly twelve intended symbol-name replacements. No exact source-plan selection or full-image identity claim is added.

Tests require mapped buffers and valid read/write indices. Native byte-count behavior through 255 is compared without claiming arbitrary corruption recovery. Queue merge/packet-flush providers, full firmware linkage, physical persistence and asynchronous scheduling/interrupt behavior remain unfinished or unverified.
