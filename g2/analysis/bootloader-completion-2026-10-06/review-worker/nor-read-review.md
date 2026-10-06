# Independent NOR read source/integration review

Date: 2026-10-06. Scope: review `g2/components/bootloader/nor_read/` against the locked stock wrapper and review the source-read integration boundary. No physical hardware access or firmware writes occurred.

## Source-to-stock findings

The candidate implements the stock `0x420F70` wrapper's observed behavior: it loads the active MSPI handle from `0x200270DC`; returns status 6 for null handle, null destination, or zero length; then returns status 5 for a start address at or above `0x02000000`. For accepted inputs, it calls the same setup/configure/delay sequence, submits one 24-byte RX PIO transfer, calls teardown, and returns the HAL status without translation. It does not add an end-address, overflow, alignment, maximum-size or chunking check. The exact command is one full-length transfer with four-byte address enabled, instruction `0x006c`, turnaround 1, and the original address and buffer.

The source marks the structure enum as the RX/TX direction and builds with `-fshort-enums`; pointer width and relevant size/offsets have static assertions. The comparison parses and compares the complete 24 command bytes, so compiler-created padding or field-layout changes in this build would fail the test. Current-source/component result hashes match: locked image `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`, component ELF `95ed294ea63882281dc57167443681482a1b5e40182af4d2a1f4114d89e06e53`, and `nor_read.c` `d55c8d97c751b9e726fe5b6f305a21d1bdfe2d42dc64d3058afcc2398d7678a9`.

The pinned Apollo510 HAL header names its `ui32Timeout` argument as microseconds. The source passes literal `1,000,000`, matching the stock value, and the test observes the argument as `timeout_usec`. Neither test runs the lower HAL timeout logic, so no statement about actual elapsed time or timeout timing should be inferred.

## Independent component rerun

Using the installed offline Unicorn environment, I independently reran `verify_nor_read.py` against the component ELF. It passed 10 original/source cases and recorded 174 distinct original instruction bytes. Evidence is saved in [nor-read-components-independent.json](nor-read-components-independent.json). Cases cover valid requests, status propagation, start exactly below/at/above 32 MiB, a request whose length crosses the address limit, null destination, zero length, and null active handle.

The independent fixture intercepts the four helper calls and the HAL transfer at their stock entries. It returns fixture-selected HAL status and records command bytes; it does not exercise setup/teardown implementations, HAL/PIO internals, or flash silicon. The crossing-end case demonstrates that the wrapper forwards the full request; the fixture is not evidence that a physical cross-boundary read would succeed.

## Integrated source boundary

The `nor_queue_runtime_task` linker module identifies NOR read as source-defined while keeping the lower local setup/configure/delay/teardown callees and `0x4262E0` MSPI blocking-transfer entry external. In `verify_arm.py --real-nor-read`, the compiled source read wrapper executes. At `0x4262E0` the fixture checks the handle and timeout, inspects command fields, and copies bytes from a memory-backed offline NOR model. The integration artifact reports 122 lower PIO reads and two kernel queue receives. These counts are synthetic-model interactions, not physical bus transactions or hardware queue operations. NOR erase/program/image readback, locks, logs, update runtime call and queue kernel paths remain synthetic providers in the described profile; no hardware timing, flash coherence, power-loss behavior, physical erase/program, or successful board boot was demonstrated.

## Limits / no blocking source defect found

The wrapper candidate is consistent with the inspected original paths and its tested command ABI. This supports only the tested compiled profile (`clang`, Cortex-M55, `-fshort-enums`, O2) and bounded fixture coverage. It does not establish all compiler profiles, exact IAR ABI or byte identity for the whole bootloader. The timeout's microsecond unit comes from the matching header comment; actual timing remains untested. The use of stock helper/HAL addresses remains an explicit unresolved dependency boundary.
