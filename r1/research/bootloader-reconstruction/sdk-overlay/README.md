# Nordic SDK on-device reconstruction overlay

> This small overlay is retained as the original correlation method. For the complete
> repository-contained build, use [`../firmware-project`](../firmware-project).

The closest source-level on-device reconstruction is Nordic nRF5 SDK `17.1.0`'s
`examples/dfu/secure_bootloader/pca10056_s140_ble/armgcc` target. Its supplied linker script already
matches the live image's core layout exactly:

- flash origin `0x000f8000`, length `0x6000`;
- RAM origin `0x20005978`;
- MBR parameter page `0x000fe000`;
- settings page `0x000ff000`; and
- UICR bootloader/MBR-parameter words at `0x10001014` and `0x10001018`.

Use the files in this directory as an overlay:

1. replace the example `dfu_public_key.c` with `r1_dfu_public_key.c`;
2. invoke GNU Make with both the vendor `Makefile` and `r1_sdk_overlay.mk`, setting
   `R1_OVERLAY_DIR` to this directory; the fragment force-includes `r1_sdk_overrides.h` without
   replacing the example's required compiler flags;
3. use the example's `secure_bootloader_gcc_nrf52.ld` unchanged; and
4. build with Arm GNU Toolchain `9-2020-q2-update` (`arm-none-eabi-gcc 9.3.1`).

From the example's `armgcc` directory, the build form is:

```sh
make clean
make -f Makefile -f /absolute/path/to/sdk-overlay/r1_sdk_overlay.mk \
  R1_OVERLAY_DIR=/absolute/path/to/sdk-overlay \
  GNU_INSTALL_ROOT=/absolute/path/to/gcc-arm-none-eabi-9-2020-q2-update/bin/
```

Do not pass `CFLAGS+=...` directly on GNU Make's command line: that turns `CFLAGS` into a
command-line variable and suppresses the vendor Makefile's required target and ABI flags.

The reference build used for symbol correlation retained ECDSA verification and produced a
symbol-bearing ELF with 321 flash functions. Its flash/RAM size report was `24016` text, `184`
data, and `21976` BSS bytes, close to the captured image's `24420` logical flash bytes and `200`
initialized-data bytes. Compiler choice, vendor modifications, and link-time optimization explain
why the images are not byte-identical.

The documented overlay build was executed successfully with the pinned SDK and compiler. It
produced the same size report and ELF SHA-256
`f105f2392c557805c93c4feb721a31449c398c044d7c410ce06c503dd3d764d3`. This hash identifies the
source-level reconstruction build; it is not claimed to match the captured retail bytes.

The captured public key is included because a verifier requires it and it is already public data.
No private key or unsigned acceptance path is present. The optional captured debug-validation
switch does not remove package-signature verification, but it is off by default because the audit
found that it weakens installed-application CRC checking.
