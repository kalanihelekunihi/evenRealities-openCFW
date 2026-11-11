# R1 motion bus request builders in C

The read/write request builders at stock `0x50188` and `0x501C8` now use C.
The 20-byte record has explicit reserved bytes/words, with compile-time
extent and offset checks. Each request starts fully zeroed, truncates the
address to eight bits and register/length to sixteen bits, stores its data
pointer in the direction-specific field, and dispatches with zero operation
and reserved arguments. It returns one only when dispatch returns zero.
The motion device cache declaration now matches its defining volatile
device-pointer cell. REA confirms the stock initialization and dispatch calls.

All 4,572 controlled record comparisons pass. These cover every byte address,
wide register/length values across truncation boundaries, null/ordinary/all-one
pointer values, four dispatch statuses and null/all-one device values. They
also repeat 576 default LIS callback cases, whose public return stays zero.
Every one of the 20 record bytes is compared, including unused-direction
fields and all reserved bytes. Register values in valid callback ranges and
full-width direct request arguments are tested separately.

Another 1,176 cases link the actual C registry dispatchers and run the stock
dispatchers, with null devices, missing slots and callable provider records.
Only the final provider operation is mocked. The candidate runs its compiled
C EABI memory-clear wrapper and upstream `memset`; no native memory helper
is linked into this candidate probe. Callback mocks poison r0–r3; r4–r11,
entry SP and eight-byte callback stack alignment pass. Record addresses and
private stack depths differ, are normalized out of public behavior equality,
and are recorded separately in the JSON.

The compiled request bodies are 72 bytes each versus stock's 60. The compiler
also inlines them into the default callbacks, which grow to 62 bytes versus
stock's 12. These are intermediate C candidates, not byte-identical providers.
The device-ID getter and identity-probe instruction bodies remain unchanged.
Physical TWI/I2C operations, DMA, sensor response, complete fault state,
concurrent cache updates and instruction timing remain unverified.

All 561 R1 units compile and both compositions succeed without duplicate
strong symbols. Actual unresolved sets stay at 238 application and 34
bootloader imports. `make sources-check` passes for both trees. No source-plan
selection or workflow gate changed.

[motion-c-requests-review.json](motion-c-requests-review.json) binds sources,
supporting C implementations, reports, stock/candidate bytes, REA results,
matrices and ignored probe hashes in `build/goal-r1-motion-requests/`.
