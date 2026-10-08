# Extended EEPROM rows and command7 persistence outcomes

Independent `extended.c` reconstructs254-byte extended-write orchestration0x8808..0x8906, next-row selection and the stock checksum span. It links the new reconstructed flash/program provider from ../touch-flash-provider-2026-10-08. Standalone ELF `3fca7b27f7624a06c2abd6b24d87b5807abe6cd4c26438a1be977b3c104e34d7`. Integrity recovery8058, historic copying814c and merge8680 remain explicit guarded test boundaries. This is not a full EEPROM provider or installed firmware.

## Layout and flow

Context offsets: u16 logical row count+0, physical row bytes+2, u32 step+4/capacity+8, wear factorbyte12, simple modebyte13, redundant-copybyte14, program modebyte15, physical baseu32+16, historic capacityu16+20, new-data capacityu16+22, last-written rowu32+24, provider pointeru32+28. These observed field roles are narrower than a complete public ABI/version identification.

Scratch row at20000cd4: checksumu32+0, sequenceu32+4, logical addressu32+8, data lengthu32+12, new payload+16, historic half starting at half-row in the coherent fixtures. Extended write uses ceil(size/new-data capacity) rows; increments sequence modulo32 for each; advances physical row by rounded-down-to4 physical size; wraps to base at base+physical_size*logical_row_count*wear_factor. It zeroes the row, writes sequence/address/length, copies new payload, invokes historic/merge helpers, computes checksum and invokes the actual program gate.

Only the final row uses remaining size as its header length; other rows use new-data capacity. Redundant mode programs the same row at an offset logical_row_count*wear_factor*(physical_size rounded-down-to4). Last-written row advances only after both program-gate calls return0. The final return prefers program-gate failure, otherwise the last merge status. Historic-copy return is ignored by this orchestration. Provider adapters can nevertheless discard lower flash errors, so a successful gate does not establish persistence.

## Exact checksum span

`CalculateRowChecksum`7f6c adds **one byte** to the row pointer, then calls CRC over row_size-4 bytes. CRC seedff, polynomial31,8 MSB-first rounds. For128-byte row it covers bytes1..124; byte0 and bytes125..127 are excluded. The remaining three checksum-word bytes are included. This agrees with the pinned public EEPROM candidate's explicit+1 byte formula; it is not a conventional four-byte checksum-field skip. Whole-row integrity/authentication strength is not inferred. A uint16 loop index constrains the bounded reconstruction to meaningful row sizes below65536.

## Fresh validation

**1,440** stock/native extended-orchestration comparisons cover logical addresses0/17, sizes1/48/49/96/145, sequence0/ffffffff, redundancy0/1, normal/wrapped last-row pointers, three merge statuses, successful/failing/mixed SROM states and PRIMASK0/1. They compare ordered boundary calls, complete row bytes, SROM parameters, context, input, SP and PRIMASK. Actual stock/native next-row, CRC, memory, program gate, row adapters, flash driver and critical bodies execute. The3 history cuts explicitly supply sequence/historic bytes/status; no historical-row recovery correctness is claimed. Physical128/new-data48/row-count4/wear2 are coherent fixture values, not verified stock configuration.

An initial60000-instruction guest limit expired during the final restore of a four-row redundant-write test (PC8da8), rather than an observed firmware timeout. It was raised to150000, and the complete suite passed. This fixture limit has no hardware timing meaning. Two mutants (checksum+4, padding final length) are rejected.

**69** separate actual stock/native checksum tests cover row sizes4..256, included-byte mutations and excluded-byte/tail mutations, with no cuts. **96** whole-stock command7 callback→deferred scenarios compare ACK preparation and later storage outcome for initialized/uninitialized storage, simple/extended mode, parameter acceptance/rejection and injected SROM failures. The simple path executes actual provider/memcpy/flash bodies without history cuts; extended retains the3 declared cuts. Sequential invocation is constructed, not task/NVIC scheduling. No physical programming or host ACK delivery occurs.

Concrete coupled result: accepted command7 prepares070017 before deferred work. With initialized storage, low flash status00520005 is discarded and application storage adapter returns0. With uninitialized storage, adapter returns1 after the same prepared ACK. Rejected zero parameter prepares07ff17 and schedules no persistence. Thus ACK cannot certify durable storage, and even the observed upper status0 can hide low-level failure.

## Remaining boundary

Integrity8058, historic814c and merge8680 algorithms remain actionable source-reconstruction leads; the current tests use explicit cuts, not invented implementations. Actual stored rows at the configured flash region are absent from the locked OTA payload, so matching live recovery requires a storage snapshot/trace or a faithful model. Physical SROM behavior, asynchronous scheduling and producing compiler/library configuration remain unverified. No global source exhaustion, whole firmware reconstruction or byte equality claim.
