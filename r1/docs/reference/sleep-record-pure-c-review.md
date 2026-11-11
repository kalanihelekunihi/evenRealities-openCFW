# R1 record-store caller and storage event in ordinary C

The record-store entry at `0x5b890` and registered event at `0x8dc94` now use C. The entire `native_sleep_record.c` unit is ordinary C. It reuses the existing sleep context and selection/write/erase components, adding no persistent state.

Store checks the initialized byte first, then rejects null input or length above 3888. It makes up to two attempts, selecting each time and using fallback only for `FFFFFFFF`. It passes the selected byte to sector-write but logs the full selected result. Any nonzero write result succeeds. After two failures it calls erase-all and logs the native flash-reset diagnostic; this does not request an MCU reset.

The event reads the halfword at offset 30, adds 32 with 16-bit wrap, and calls store. It notifies type 6 only on success. Null input and storage failure retain their separate diagnostics.

Validation passes 31,104 stock/C comparisons covering all 416 native instruction bytes, initialization/length priority, both attempts, signed index handling, nonzero write results, event length wrap, mutable owners/input, logging variants and caller guards. Another 3,456 cases execute the C record/event, selector/fallback, write/finalize/count/erase, CRC and memory-clear graph against a mutable flash model. Flash bytes and all modeled calls/logs match. Ten compiled defects are rejected.

The previous caller assembly advertised two-byte section alignment while its literal loads required a four-byte-aligned entry. C compilation now supplies four-byte section alignment and removes the legacy log-constant linker dependency. Both direct and full-chain fixtures use the default linker layout, without a custom parent-alignment script. This closes that caller-specific issue; it does not establish a final bootable image.

The tested objects match the normal build. The other 852 prior nongenerated objects remain identical. Existing count/erase/thunk section bytes and normalized relocations are unchanged; other preexisting C source text is unchanged. The scan/delete entries also pass 288 stock regression comparisons in the new unit. The manifest, source-plan selections, imports and persistent state remain unchanged: 863 compiled units, 63 application imports and 22 bootloader imports.

[The receipt](sleep-record-pure-c-review.json) records hashes and proof boundaries. FAL read/write/erase, logging and health notification remain modeled in the full-chain fixture. Physical NOR operation, power-loss behavior, concurrency, final application linking and boot remain unverified. Other firmware assembly remains separate work.

The subsequent [C sync-marker backend](sleep-sync-marker-pure-c-review.md) extends the actual storage-chain fixture through acknowledged-header marker programming with the existing context owner.
