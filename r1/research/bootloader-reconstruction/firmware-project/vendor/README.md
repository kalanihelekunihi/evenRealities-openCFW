# Vendored nRF5 SDK dependency closure

This directory contains the minimal dependency closure exercised by the R1 secure-bootloader build,
not the complete 623 MiB SDK distribution. It was selected from a clean nRF5 SDK 17.1.0
`pca10056_s140_ble` reference build's compiler dependency files, with linker scripts, build helpers,
licenses, crypto libraries, and the S140 7.2.0 HEX added explicitly.

Contents:

- 316 files under `nrf5-sdk/`;
- 73 upstream C/assembly units used by the target;
- headers reached by those compilation units under the recovered configuration;
- Nordic's unmodified secure-bootloader linker script and GNU Make helper;
- the licensed CC310 BL and Oberon object libraries supplied with the SDK; and
- the matching S140 7.2.0 runtime HEX and license.

`vendor-files.txt` is the authoritative path inventory. `vendor-sha256.txt` pins every byte. Verify
the closure with:

```sh
python3 ../tools/vendor_sdk_subset.py --verify-only
```

To regenerate it from an already-built pristine SDK reference:

```sh
python3 ../tools/vendor_sdk_subset.py \
  --sdk-root /absolute/nRF5_SDK_17.1.0_ddde560 \
  --dependency-dir /absolute/reference/armgcc/_build/nrf52840_xxaa_s140
```

The regeneration tool deliberately excludes the SDK example's generated `dfu_public_key.c`; the
project supplies the R1 public key as recovered product data instead.
