# Correct native VPMIC sense ADC ownership

The native `0x506a4` reader now uses `r1_yhm_transport_context + 16`, the
`vpmic_isns_adc` handle initialized by `r1_yhm_device_handles_initialize`.
It previously used the separate battery-runtime ADC field. The historical
frontier/function name `r1_battery_voltage_read` remains, but it does not
establish physical units or make this the `vbat_adc` path.

The two authenticated contexts are adjacent, distinct storage owners:

| Context | Base | ADC field | Registry name |
| --- | --- | --- | --- |
| YHM transport | `0x2000687c` | `0x2000688c` | `vpmic_isns_adc` |
| Battery runtime | `0x20006890` | `0x200068a0` | `vbat_adc` |

REA verified the reader's context literal, the YHM initializer and its lookup
name, and the battery ADC cache's different base literal. The existing C owners
are retained. The fix changes the reader's symbol relocations from the battery
runtime owner to the YHM owner; function code bytes remain identical.

The prior one-context fixture relocated the battery-runtime symbol to the YHM
address, masking this error. Its arithmetic and frame comparisons were narrower
than correct composition binding. With both contexts present and different
handles, the previous object fails immediately: it opens `0x20005000` while stock
opens the YHM handle `0x20004000`. The earlier review is marked superseded for
that hardware binding claim.

The corrected object passes 10,240 direct paired comparisons. Another 6,656
paired comparisons execute the actual YHM C initializer before acquisition,
covering cached handles and `vpmic_isns_adc` lookup misses with caller-clobbering
lookup callbacks. Both contexts coexist at their authenticated addresses. The
battery runtime's guards and handle remain untouched, including while ADC
callbacks change the YHM handle. The original 24-byte frame, partial scratch
word, signed clamping, integer conversion, raw status policy, live registers,
returns, stack and masks remain checked.

All 579 R1 units compile and compose without failures or duplicate strong
symbols. The 578 unrelated objects are unchanged, imports remain 164 application
and 34 bootloader, and the manifest changes only the explanatory ADC note.
Scoped qualification compiles the unit but selects no exact region. Strict GCC
still uses a 32-byte provider frame instead of 24 and remains unqualified.

The source plan and canonical hybrid application remain unchanged: SHA-256
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`,
4,043 selected source bytes, 642,117 binary fallback bytes and 248 resource bytes.
The normal report is `build/sources-goal-r1-vpmic-binding-c-final/report.json`.

[Machine-readable evidence](vpmic-binding-c-review.json) records REA observations,
source/build hashes and the retained regression. Probes live under ignored
`build/goal-r1-vpmic-binding-c/`. Registry lookup and ADC providers are modeled;
physical ADC accuracy, final linker placement, arbitrary private-frame aliases,
faults and concurrency remain unproven. Original Arm Compiler 5 is unavailable.
Complete source-only, byte-identical firmware remains incomplete.
