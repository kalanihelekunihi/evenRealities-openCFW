# Bootloader startup source slice

`initialize.c` reconstructs the image's compressed-record expansion and zero-table helpers. `record_dispatch.c` adds the slot-relative callback walker at `0x43299c` and vector-base initialization at `0x432910`. `system_entry.c` reconstructs the `0x43297c` chain, with system initialization and terminal explicitly unresolved. `fpu.S` reconstructs `0x432958` CPACR/FPSCR setup. `record_adapters.S` translates the stock implicit R9 static base to the C helpers' explicit second argument; it preserves stock callback locations for the locked fixture table.

The walker visits `0x4330d8..0x433120`. First callback zeroes RAM ranges `0x2000055c + 0x26c6c` and `0x20081000 + 0x74100`; subsequent callbacks expand 22 compressed bytes to 24 ITCM bytes at `0x40`, 625 bytes to 1,371 RAM bytes at `0x20000000`, and 48 bytes to 4,096 RAM bytes at `0x20080000`. Each callback returns the next record, so this is a scatter-initialization table, not a conventional constructor array.

The vector initializer sets VTOR to `0x410000`. The separate reset literal `0x2007d000` is a stack limit. FPU setup ORs CPACR with `0x00f00000`, performs DSB/ISB and writes FPSCR `0x02040000`.

Build and offline comparison:

```sh
make -C g2/components/bootloader/startup records CPU=cortex-m4 OUT=../../../build/bootloader-completion/startup-records-compatible
~/.local/share/opencfw/venv/bin/python g2/components/bootloader/startup/verify_records.py \
  --elf g2/build/bootloader-completion/startup-records-compatible/records.elf \
  --output g2/build/bootloader-completion/startup-records-compatible/comparison-fpu.json
```

Current result: seven original/source cases pass, executing 276 distinct original instruction bytes. Direct dispatcher/helper/vector/FPU cases have no returning provider stubs; the system-entry case intercepts system-init and terminal and checks call order/argument0. Original and source FPSCR read back `0x02000000` under Unicorn, masking bit18; this validates matching emulator behavior and exact write instruction, not silicon FPSCR semantics.

The authenticated official table and compressed streams are fixture data copied only by the verifier. They are not embedded executable donor data in source and their compressed representation is not source-generated. Full reset, stack-limit setup, clock/system provider closure, kernel/IRQ entry and a bootable image remain outstanding. The Cortex-M4 comparison profile does not establish Cortex-M55 compiler/ABI equality, byte identity or hardware bootability. Older helper/profile receipts may have stale source hashes after these additions; use the latest matching receipt for current claims.

`reset.S` additionally reconstructs the M55 stack-limit entry and stack-pattern/PSP/FPU/system-entry chain. `make -C g2/components/bootloader/startup reset-source OUT=../../../build/bootloader-completion/startup-reset-m55` compiles and links this source for Cortex-M55. This is a compile-only result: MSPLIM/PSPLIM operations and the complete reset chain have not been executed or compared in the compatible M4 fixture. The linker entry remains a callable source slice, not a production vector-table/bootable image.

The source-table profile now replaces the 72-byte record fixture with linked
`init_records.S` data at `0x4330d8`. Its bytes match the locked table exactly
(SHA-256 `6b49c166db580b208c6fdbac81858b42603f164b9caf0f065507836def88cfa9`).
Build with `records-table`, then invoke `verify_records.py --source-table`
against `records-table.elf`. Seven cases/276 original instruction bytes pass.
Source-side input copying is limited to the three compressed streams
(22+625+48=695 bytes); unused image-suffix data is no longer copied. The table
is source-defined data, not added instruction coverage, and the streams'
compressed representation remains unresolved.
