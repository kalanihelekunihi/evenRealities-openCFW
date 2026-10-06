# Stock MSPI command-queue initializer wrapper

`mspi_cq_init.c` reconstructs the 44-byte stock wrapper at
`0x00423f28..0x00423f54`. The source image is the authenticated
`g2-2.2.6.10/ota_s200_bootloader.bin` (SHA-256
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`). The
function bytes hash to
`8e2e5409620c3c1b334d8c3ede2ea19b20a31471e40a0c8b0c88f6550a7e9b05`, matching
`g2/symbols/bootloader.tsv`. See `stock-disassembly.txt` for the original
Thumb instructions and literal.

The wrapper builds a stack config prefix from its three arguments and calls
`am_hal_cmdq_init` at stock `0x00427794`:

| Value | Stock operation |
|---|---|
| interface | `(module + 8) & 0xff` |
| config word at+0 | `queue_size_input >> 1` |
| config word at+4 | forwarded queue-buffer address |
| config byte at+8 | `1` |
| output handle slot | `0x2001caa0 + module * 0x8d0 + 0x828` |

The absolute base comes from the function's literal `0x2001caa0`; the stride
and field offset are formed as `module * 0x8d0` and `+0x828` in the stock
instructions. The stride and slot offset match the sparse state extent used
by separate MSPI lifecycle analysis. The absolute base is specific to this
bootloader image, not an application-firmware profile. This establishes the
exact pointer target for this wrapper, but not semantics for the complete
MSPI state or queue object.

The stock wrapper writes only byte+8 of the config prefix after storing the
first two words. Bytes+9 onward overlap saved stack-register storage in the
stock prologue. The source represents only the known word/word/byte fields;
the test compares those first nine bytes. The stock consumer at `0x427794`
loads byte+8 with `ldrb`, so the overlapping bytes are not consumed by that
field. No source reconstruction or behavioral test for the consumer is
claimed. The downstream return is not checked by the parent enable path; this
C wrapper is `void` and does not define a return contract.

## Build and comparison

`make` builds an ARM Cortex-M55/Thumb/soft-float ELF. Run the bounded
original/source fixture with:

```sh
make PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python test
```

The test passed eight cases and reached all44 distinct stock instruction
bytes. It compares the arguments observed at the external `am_hal_cmdq_init`
boundary: interface byte, config word+0, config word+4, config byte+8, exact
output-slot address, and seeded output-slot contents. Cases include modules0,
1,2,3,255 and `0xffffffff`, shift edge values, different queue-buffer
addresses, and lower-provider statuses0,1,3,7. The provider returns the chosen
status but does not initialize a queue or write the output slot. Evidence is
`out/comparison.json`.

This supplies readable source for the exact wrapper called by stock
`am_hal_mspi_enable`, with one explicit remaining boundary: the real
`am_hal_cmdq_init` body at `0x00427794`. No SDK implementation, queue data
structure behavior, allocation, hardware access, startup, or byte-identical
build is claimed.
