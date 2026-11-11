# Clock-invalid guards and offline enqueue in C

The four guarded dispatch imports now resolve to ordinary C at `0x8d538`, `0x8e27c`, `0x8d6d8` and `0x8a64c`. Their lower enqueue functions at `0x3fba4`, `0x43da4`, `0x40a88` and `0x3bee4` are implemented together. The hourly readers include the shared typed API; their compiled object remains identical. No executable stock binding, allocation or extra lock is introduced.

Guards preserve null/slot checks, the inclusive `0x38640900` timestamp limit, fresh clock reads, future-record precedence over future-day rejection, stock log strings and severity metadata. HR/SpO2 guards intentionally leave the slot limit to enqueue; HRV/activity check it before reading the clock. Activity expands an accepted hour into six four-byte records at byte indices `hour*6+i`, preserving each lower enqueue's fresh clock sample and zero-data rejection.

The recovered source storage has one owner per region:

| Queue | Record base | Record stride / capacity | Cursor (read, write, count) |
| --- | --- | --- | --- |
| HR | `0x2001576c` | 16 / 24 | `0x20006798` |
| SpO2 | `0x200158ec` | 16 / 24 | `0x2000679b` |
| Activity | `0x20015a6c` | 16 / 144 | `0x200067a8` |
| HRV | `0x2001636c` | 20 / 24 | `0x200067ab` |

These regions do not overlap another existing source owner. The [REA literal read](health-offline-enqueue-c-rea.json) confirms the HR record/cursor pair; all eight addresses are checked against locked Thumb literals. Records lie in the authenticated scatter zero region `0x20007e04..0x2003beb8`. Executing the actual stock decompressor `0x286f4` over the `0xc4610` initialization stream confirms all four cursor triples are zero and matches the independently decoded 6,492-byte initialization span by SHA-256. Source storage totals 3,564 bytes, with unique strong symbols verified by audit.

Enqueue preserves the native payload widths, offset/slot truncation, untouched padding, day/timestamp metadata and store order at the C access level. HR/SpO2 require a nonzero first byte, HRV a nonzero first halfword, and activity a nonzero word. Full queues advance the read cursor while replacing the oldest entry; counts increment only below capacity. No synchronization behavior beyond stock is claimed.

The [machine-readable receipt](health-offline-enqueue-c-review.json) records 2,244 direct stock/C comparisons and 2,265 source clock calls across future-time rejection, priority/logging, slot limits, empty/null data, record aliases, padding, ring wrap, overwrite-on-full, offset truncation and repeated fills. Another 830 reader/hourly-storage comparisons execute the actual guards and enqueue bodies, including invalid-clock appends, retry and midnight clearing. Only clocks, logging, allocation and outer FlashDB boundaries are modeled in that integration; dispatch is not replaced by a stub.

Six separately compiled defects fail runtime assertions: wrong guard threshold, wrong future-day boundary, missing HRV slot check, wrong activity sub-index, missing full-ring read advance and truncated offset width. All 738 prior objects remain identical. `make sources-check` passes; 665 application and 74 bootloader units compile/compose with no failures or duplicate strong symbols. Application imports fall from 159 to 155 with no added imports; bootloader imports remain 34.

Tests require valid initialized read/write cursor indices and mapped SRAM. Native byte behavior for counts above capacity is compared, without claiming recovery from arbitrary corrupted cursor indices. Other queue consumers, asynchronous IRQ/scheduler behavior, complete firmware linkage and physical persistence remain unfinished or unverified. No exact source-plan selection or image-integration claim is added.
