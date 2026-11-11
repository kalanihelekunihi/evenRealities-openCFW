# R1 Goodix transport cold-state correction

The shared request in `r1/src/application/goodix/stock_i2c_transport.c` now
starts with address byte `0x24`, write length one, and read length one.
The previous implicit zero initializer differed from stock startup data.
All other request bytes and the adjacent bus/IRQ/callback/reset words start
at zero. The callback producer remains unresolved; its cold value is not
evidence of the absence of later writes.

The ignored probe `build/goal-r1-goodix-cold-state/verify.py` freshly executes
the locked image's loader from `0x283a1` to `0x27208`, stopping before product
runtime. The copied-data destination is prefilled with `0xa5` to avoid a
zero-filled emulator mapping concealing an initialization failure. The stock
application SHA-256 is
`0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a`.

The 20 initialized request bytes at `0x200076dc` are:

```
24 00 00 00 00 00 00 00 01 00 00 00 00 00 00 00 01 00 00 00
```

These are ordinary mutable request data, not executable bytes. The C object
expresses the values as typed field initializers. The linked C initializer
matches all 36 bytes from the bus handle at `0x200076cc` through the end of
the request. A deliberate source variant restoring zero initialization is
rejected by this comparison.

Eight first-transfer comparisons start both executions from that stock cold
state and execute native/C read or write request helpers with null cached bus
handles. The request writes still occur before registry dispatch. This covers
retention of the opposite direction's initial length, as well as null/non-null
buffers and truncated command/address/length words. Cold address `0x24` is
not assumed to be the runtime Goodix address; transfer helpers overwrite it.

Current objects also pass 630 transport cases, 1,536 binding/transport/reset
sequences and 2,592 IRQ comparisons. The full R1 build at
`build/sources-goal-r1-goodix-cold-state/report.json` compiles 564 units,
without failures or duplicate strong symbols; imports remain 210 application
and 34 bootloader. `make sources-check` passes.
[Machine evidence](goodix-cold-state-review.json) binds the loader/ELF check,
negative control, regressions, source and build reports by hash.

The test linker places these sections at native addresses only for the
comparison. Final firmware source linking, electrical operation and whole
image byte identity remain unproven; the canonical source plan is unchanged.
This is no global source-completeness or G2 workflow-gate advancement.
