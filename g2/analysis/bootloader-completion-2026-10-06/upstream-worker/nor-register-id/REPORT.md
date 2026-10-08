# Indexed register read at `0x41d90e`

Added [register_id.c](../../../../../components/bootloader/nor_mspi_init/register_id.c)
and its header as a small provider for the currently integrated symbol
`opencfw_read_mspi_register_id(register_id, out_value)`. It preserves the
stock behavior:

- IDs `0..0xdf`: if `out_value` is null, return 6; otherwise read one volatile
  32-bit word at `0x40010000 + register_id * 4`, store it, and return 0.
- IDs `>= 0xe0`: return 5 before testing `out_value` and perform no MMIO read.

The locked instruction at `0x41d90e` loads literal `0x40010000` from stock
data address `0x41e110`; the following indexed load is a 32-bit read, not a
lookup in a source-side constant table. I preserve that as a raw register
region. The function’s existing `read_mspi_register_id` integration name does
not establish that the address is an MSPI peripheral block: the pinned SDK
5.1 CMSIS header names MSPI0 at `0x40060000` (`apollo510.h` lines 29558–29561,
SHA-256 `b6ca35dc828ef95825c0a22f06e6ca5ed558a6542dc74310515fdc350051a797`).
The observed `0x40010000` base remains unnamed.

The standalone original/source differential passes all 224 valid IDs and six
boundary/null cases. Each valid case initializes the raw region with a
deterministic synthetic word and checks the returned word plus exactly one
32-bit read at the expected address. Invalid/null paths are checked for their
status and absence of a read. It traces 30 distinct original instruction
bytes. No peripheral behavior is inferred from the synthetic Unicorn RAM.

Run with:

```sh
make verify PYTHON=/Users/kalani/.local/share/opencfw/venv/bin/python
```

The machine-readable receipt, locked-image SHA, ELF SHA, and per-source hashes
are in [comparison.json](out/comparison.json). The locked image is
`f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`.
