# Bounded IAR runtime object comparison

## Result

The original installed archive is present at `third-party/local-vendor/toolchains/iar-linux-x86_64/cxarm-10.10.2/arm/lib/dl7M_tlng.a` (1,197,398 bytes; SHA-256 `a7a547ad93e3646009705a608f1f5421e9390ba67682206e9e2a726c9262c81c`). The probe extracted 21 named members, including the formatter wrappers and variants, secure memory operations, xxmem operations, float classification helpers, and floating formatter code.

The report analyzes 37 genuine `.text` `STT_FUNC` entries with a nonzero declared ELF function size of at least 16 bytes. For each entry, it gathers every decoded instruction in the full declared `[start, start + st_size)` extent, across local IAR labels. Zero-size `??...` fragments are excluded as independent candidates. The sample includes `printf`, `sprintf`, `snprintf`, `memcpy_s`, `memset_s`, `__data_memcpy`, `__iar_i_fpclassify32/64`, and formatter backends.

The installed IAR 10.10 `snprintf` body is 68 bytes; the `_Printf` body in `xprintfdefault.o` is 2,988 bytes. The corresponding stock entries are 62 bytes at `0x41b218` and 3,256 bytes at `0x41e47a`. Across the 37 functions and two stock extents with known size, all 74 comparisons were negative for exact size and coarse full-body mnemonic-sequence equality. No match or source identity is claimed. Stock `vsnprintf` at `0x41b25c` remains an explicit unresolved-extent negative because no stock size was supplied.

The stock disassembly records 29 instructions / 2 estimated blocks / 1 CFG edge for the 62-byte `snprintf` entry, and 1,270 instructions / 318 estimated blocks / 407 edges for the 3,256-byte backend. These are disassembly-derived structural summaries, not recovered pseudocode.

## Reusable extractor

`iar_shortcut.py` extracts only the named members from the supplied `.a`, hashes them, reads function symbols from ELF metadata, and collects section tables, relocation records, `.iar.rtmodel`, `.iar.stackusage`, and `.debug_frame`. It compares only after verifying the stock image SHA-256. It never invokes the IAR compiler, imports runtime source, or reads compiler credentials.

```sh
python3 iar_shortcut.py \
  --archive ../../../../../third-party/local-vendor/toolchains/iar-linux-x86_64/cxarm-10.10.2/arm/lib/dl7M_tlng.a \
  --objects /tmp/opencfw-iar-runtime-objects \
  --stock ../../../../blobs/official/g2-2.2.6.10/ota_s200_bootloader.bin \
  --out report.json --limit 50
```

The object hashes for the seven members already present in `sdk-probe-evidence.json` match all seven recorded values. The archive digest is stored in `report.json`.

## Validation and limits

The original archive yielded all 21 requested members. The stock image matched the locked SHA-256 `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5`. A one-byte mutation of a temporary stock copy made the helper stop with the expected locked-hash mismatch. Report assertions confirm 37 nonzero-size function entries, 74 comparison pairs, zero exact-size pairs, zero coarse sequence matches, and nonempty `.iar.rtmodel`, stack-usage, and debug-frame metadata.

The mnemonic fingerprint is intentionally coarse: it does not normalize operands, literal pools, relocation sites, or compiler code-generation differences. CFG counts are approximations from decoded branch targets. The stock compiler is only attributed as an unconfirmed EWARM 9.60.2 candidate, while the inspected objects are IAR Base 10.10.2.27058. The runtime source license restricts source use to IAR products; this work uses object metadata and disassembly only. Object identity does not close source reconstruction or byte equality.
