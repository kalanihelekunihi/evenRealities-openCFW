# QMA6100 ordinary C interrupt entry

`r1/src/application/runtime/native_qma_transport.c` replaces the naked IRQ
entry with a C local status word passed to the existing canonical
`r1_qma_irq_body`. That body writes zero to the entire word before the first
read. No incoming register seed or old stack bytes are needed. The chip-ID and
FIFO entries still require their saved-byte fallbacks and retain their adapters.
The callback-result gateway also remains: callbacks have void C signatures,
while the raw IRQ entry returns the last tap callback's machine result.

The only repository caller is `r1_qma6100_interrupt_wrapper` in
`native_motion_selection.c`; it uses ordinary C calls and discards the IRQ
result before releasing the bus. It does not consume incidental R3 restoration.
The new entry preserves R0, normal callee-saved registers, SP, interrupt masks,
callback alignment and dispatch behavior. Its private scratch address and R3
contents are no longer part of the interface. Retained pointers from modeled
callbacks follow the actual buffer address rather than a fixed stack offset.

Fresh REA evidence covers the complete 72-byte stock entry at 0x86fa8 and
matches the preserved raw application. The test executes actual stock/C read
retry loops against modeled bus, delay and event callbacks. An independent
byte/status oracle checks partial and non-writing reads, retry exhaustion,
all 256 values of each dispatch byte, null handlers, all 50 bus-success
positions, live sensor address changes and handler replacement. Any-motion
callbacks can change retained status bytes and the live tap pointer; dispatch
reloads both. Full-width callback results and final status match.

The final normal product object passes **4278 paired cases (8556 executions)**.
Source execution is prohibited from entering stock instruction addresses. Five
compiled defects are detected: missing initial zero, shortened retry count,
incorrect motion mask, stale tap byte and incorrect null-tap result. The new
root is the only changed allocated section/relocation set within the QMA unit;
all other transport, FIFO, chip-ID and callback gateway sections are unchanged.

The fresh normal build compiles all **800 units (718 application, 82
bootloader)** with zero compile failures or duplicate strong symbols. Imports
remain 96 application and 22 bootloader metadata symbols. All 797 other
nongenerated object hashes are unchanged; generated boot vectors/crypto retain
identical allocated bytes and relocations. Strict GNU bootloader linking passes.
R1 manifest checks pass; the global check retains the unrelated unlisted G2
`resident_rom_thumb_set.S` file. No source-plan selections are changed.

[Machine-readable evidence](qma-irq-pure-c-review.json) records exact hashes and
receipts. This supersedes the IRQ bridge description in
[qma-c-irq-review.md](qma-c-irq-review.md). Physical IRQ delivery, electrical bus
behavior, delay timing and full application final linking remain unverified.
Private frames, incidental R3, faults, arbitrary aliases and concurrency are
outside the comparison scope. Bus, delay and event providers remain modeled.
