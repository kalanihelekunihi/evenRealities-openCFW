# Register-setting selector at `0x41fadc`

Added a readable provider in
[`mode_publisher.c`](../../../../../components/bootloader/clock_manager/mode_publisher.c)
and a small ABI wrapper in
[`mode_publisher_abi.S`](../../../../../components/bootloader/clock_manager/mode_publisher_abi.S).
The wrapper retains stock `push {r7,lr}` / `pop {r0,pc}`, which returns the
saved R7 value. The C core implements the module/selector dispatch and issues
the observed ordered `(register_id, value)` calls to the already-recovered
`opencfw_bl_power_register_update` source in `clock_class_providers.c`.

The raw call graph shows module as an untruncated word; only the mode argument
is `UXTB`-truncated. Modules 0 and 1 select the recovered register sequences;
all other module values return without updates. The value pointers loaded from
the stock literal pool resolve to volatile runtime words at
`0x20000000..0x20000074`. The provider reads those exact locations each time it
issues an update. This component does not claim or provide their startup
initialization.

The standalone M33 Unicorn differential compiles the C core, wrapper, and the
existing lower power-register provider. Both stock `0x41fadc` and its actual
lower helpers at `0x41d92c` and `0x41b8ec` execute as original instructions.
All 256 byte selectors run for modules 0 and 1; additional fixtures cover
module 2/3/4, invalid modules, and upper-bit selector truncation. It compares
return R0, SP, callee-saved registers, PRIMASK, runtime-value reads, the full
synthetic register block, and ordered register writes. All 563 cases pass,
covering 664 distinct original instruction bytes. A mismatch found during
development for module 1 selectors 6/8/0x16/0x18 was corrected: those paths
apply the 0x63–0x66 group, then 0x61/0x62, then the common updates.

MMIO and runtime configuration words are synthetic memory. The test establishes
the recovered code/data flow only; it does not establish physical peripheral
behavior, the real startup provenance of the values, timing, or selected
hardware mode. The receipt, source ELF SHA, and file hashes are in
[`comparison.json`](out/comparison.json). Locked image SHA-256:
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.

Run with:

```sh
make verify PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python
```
