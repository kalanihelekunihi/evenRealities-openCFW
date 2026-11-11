# R1 sleep-sector selection and fallback in ordinary C

The selector at `0x8fe28` and fallback at `0x8fc6c` now use C. They reuse the existing sleep context and sector-count core, adding no persistent state.

Selection accepts the first header with word 0 equal to `FFFFFFFF`, words 1 and 2 both equal to `FFFFFFFF`, or word 0 equal to `CCFFAABB` with word 1 different from `66889977`. Results sign-extend a byte, including indices 128..254. Header scratch initializes once and retains untouched bytes across partial or failed reads.

Fallback chooses the first smallest unsigned counter at word 2 without checking magic. It converts the chosen index to a byte, queries the live sector count again, and uses sector 0 when out of range. It still issues a 4 KiB erase for count 0 and ignores erase status. Diagnostic offsets reload the live base after the erase and logging callbacks; they can differ from the original command address.

Validation passes 17,200 stock/C comparisons covering all 346 native instruction bytes, every selectable index, header predicates, ties, partial reads, live provider/count changes and logging variants. Another 1,728 cases execute the record-store parent, C selector/fallback, write/finalize/count/erase, CRC and memory-clear routines against a mutable flash model. Flash bytes and all modeled calls/logs match. Nine compiled defects are rejected.

The tested object matches the normal build. The other 852 prior nongenerated objects, strong-symbol set, manifest, source-plan selections, imports and persistent state are unchanged: 863 compiled units, 63 application imports and 22 bootloader imports.

The retained record-store assembly advertises two-byte section alignment, but its PC-relative literal loads require a four-byte-aligned entry. The integration fixture explicitly supplies and asserts that alignment. The subsequent [record-caller C conversion](sleep-record-pure-c-review.md) removes this dependency and verifies the full path with the default linker layout.

[The receipt](sleep-sector-select-pure-c-review.json) records hashes and proof boundaries. FAL and logging are modeled. The flash model does not establish physical NOR behavior, power-loss safety, concurrency, final linking or boot. Preserved signed-byte and zero-count erase behavior is compatibility evidence rather than a safety guarantee.
