# R1 legacy 0xf2 dispatch in C, 2026-11-11

Stock `0x62c30` indexes a 72-word RAM callback table at `0x20006c60`.
Decoding the locked application's compressed RW initializer at `0xc4610`
produces exactly 15 nonzero slots: selectors 0, 1, 2, 3, 4, 5, 6, 8, 9, 18,
27, 31, 44, 48, and 71. The C switch in
`r1/src/application/board/native_legacy_f2_dispatch.c` routes those entries
to their stock child behaviors. Empty slots and selectors outside the table
return zero. This preserves the initialized table rather than treating every
selector as empty; the search for direct literal references found only the
dispatch load at `0x62c44`.

The implemented entries return Goodix, motion, YHM, battery, temperature,
touch and NFC status; issue ship/reset operations; select a Goodix PPG mode;
or register the five-sample `gray` factory stream. The gray callback copies
each twelve-byte sample, sends samples two through four, then unregisters
on sample five. The battery-voltage child clears the first 51 bytes of the
existing source-owned device context before refreshing and reading the
offset-42 halfword. The gray handle is a separate source-owned word
corresponding to native `0x20006c50`; the source linker does not place it at
that stock address. The reset child uses the existing C reset wrapper.

The ignored host probe at `build/r1-f2-dispatch-c-20261111/probe.c` checks
all 72 slots, their reply lengths and key payload bytes, ship/reset order,
three Goodix mode choices, and the gray stream lifecycle. It passes
AddressSanitizer and UndefinedBehaviorSanitizer. The host compilation uses
an ignored copy with only the ARM battery-context header and ELF section
attribute adapted for macOS; the actual ARM source separately compiles in
the R1 manifest. Callback timing, flash writes and physical reset behavior
remain unverified.

`build/sources-r1-f2-dispatch-c-20261111/report.json` compiles 938/938
application and 82/82 bootloader units with no known failures or duplicate
strong symbols. The strict application receipt at
`build/r1-link-f2-dispatch-c-20261111/report.json` has 13 undefined
functions and uses 644,016 of 696,320 flash bytes without overflow. The
strict bootloader receipt at
`build/r1-boot-link-f2-dispatch-c-20261111/report.json` links with a valid
vector. Byte identity is not established.
