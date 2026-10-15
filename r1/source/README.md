# R1 source candidates

`r1_crc.c` and `include/openr1/r1_crc.h` restore the exact files from
commit `832137ec` (`r1/src/r1_crc.c` and `r1/include/openr1/r1_crc.h`).
They supply the missing dependency of `gomore_primitives_pkey_load`.
The stock contract at `0x0006AD80` requires a non-reflected CRC32C with
initial state zero; see
`r1/docs/correlation/GOMORE-PRIMITIVES-REDUCTION-CORRELATION.md:865-880`.
This restoration does not establish instruction identity or stock placement.

Run `make -C r1 source-candidates` to compile all reconstructed provider units
and these source files to ARM Cortex-M4F ELF objects using Clang. The report at
`r1/research/source-build/report.json` records input/compiler/object hashes,
commands, diagnostics, definitions and remaining runtime references. A failed
unit removes its previous object and fails the command. This target is a compile
audit, not an application/bootloader link or an Arm Compiler 5 matching build.

`stock_checksums.c` adds three stock-shaped entry points with uint32 lengths:
CRC-16/MODBUS (`0x0005D87C`), caller-seeded CRC-32C update (`0x0005D8A4`),
and wrapping base-131 byte hash (`0x0005D8CC`). Unlike the historical CRC helper,
the update entry point retains the stock writable state-pointer ABI.
`generate_stock_checksum_tables.py` produces tables from named polynomials;
`verify_stock_checksums.py` authenticates both complete tables against their
image pointers and checks compiled C against the stock Thumb routines with
Unicorn. Empty, fixed, random and 4,096-byte inputs plus nonzero CRC seeds are
included. Run with a Python environment containing `unicorn==2.1.4`:

```
python r1/tools/verify_stock_checksums.py
```

These tests establish observed behavior for the tested inputs, not instruction
identity, proof for all inputs, or firmware integration. The generated tables
are data with declared algorithms, not retained opcode arrays.
