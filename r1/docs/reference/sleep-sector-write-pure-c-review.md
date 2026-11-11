# R1 sleep-sector programming in ordinary C

The assembly entry at `0x8fe98` is replaced by C in `native_sleep_sector_write.c`. It scans up to eight slot headers, programs the payload first, fills the metadata and CRC, then programs exactly 20 header bytes. It uses the existing context, CRC16, memory-clear and finalization boundaries.

A free slot requires both words at offsets 8 and 12 to equal `FFFFFFFF`. Scratch is initialized once and retained between reads. The initial header address stays fixed; occupied headers select the next payload address using the live partition base. Device callbacks reload at every read/write boundary. Input metadata loads after payload programming, and the header-write callback reloads after CRC calculation.

The native alignment expression is `(length+3)&0xfffc`, including 16-bit wrap. Only a zero FAL write status succeeds. Overflow requests sector finalization and returns 0. A successful final slot returns the full finalizer result; other successful slots return 1. These native rules are preserved. Callers must supply a valid source extent of at least `max(20, aligned_length)` and valid live providers.

Validation passes 9,922 stock/C comparisons covering all 508 native instruction bytes, every slot, both free-marker words, failure statuses, partial reads, alignment/address boundaries, logging and finalizer results. Another 144 comparisons change partition/device/input state at distinct read, payload and CRC boundaries. Another 648 cases execute the record-store parent with the C write, CRC, memory-clear and erase/count routines. Eight compiled defect variants are rejected.

The tested object matches the normal build. All 852 other prior nongenerated objects remain identical. The public success-diagnostic bytes and strong-symbol set are unchanged, and the unit adds no writable state. The manifest, source-plan selections and imports are unchanged: 863 compiled units, 63 application imports and 22 bootloader imports.

[The receipt](sleep-sector-write-pure-c-review.json) records hashes and proof boundaries. FAL I/O, finalization and logging remain modeled boundaries. Physical NOR programming, power-loss behavior, concurrency, final source linking and boot remain unverified. The subsequent [C finalization conversion](sleep-sector-finalize-pure-c-review.md) closes that assembly boundary and adds an actual write/finalize-chain comparison.
