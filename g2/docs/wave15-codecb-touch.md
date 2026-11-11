# Wave 15

Final links: g2/build/g2c-w15-final-{touch,em9305,codec-a,apollo-main,apollo-bootloader} and g2c-w15-final-codec-b2 (codec-b). All six have 0 undefined symbols.

## codec-b fits the stock bound
- Profiles g2-codec-b-1/2/3 changed from -O2 to -Os. The image end moved 0x10018c18 -> 0x100175bc. No memcpy PROVIDE was needed (0 undefined).
- backup_runtime_printf.c now defines PRINTF_DISABLE_SUPPORT_FLOAT and PRINTF_DISABLE_SUPPORT_EXPONENTIAL. Evidence from the decompile corpus open-2026-09-29/image_b_sram:
  - _out_rev at 0x10008a04 is called only by ntoa_format at 0x10008aa0, so upstream _ftoa/_etoa (which also call it) are absent.
  - No image-B decompile contains a double.
  - Removing them drops _ftoa, _etoa and the soft-double helpers.
- Result: image end 0x10016cd8, 948 B under 0x1001708C. bin 81,112 B vs stock 82,060 B. The ld now has an ASSERT for the bound.
- No fixtures were removed.

## touch
- SystemCoreClockUpdate now has a body, rebuilt from stock 0x4734..0x4768. It matches upstream system_cat2.c (HF frequency, Mhz/Khz round-up, and Khz<<15 for cy_delay32kMs).
- The 36 B gap 0x20000884..0x200008a8 is unused padding:
  - The only stock words that point into it are 0x20000884, which is __TMC_END__ in crtbegin's tm_clones code (an empty table).
  - No stock word points inside the gap.
  - It is now reserved NOLOAD as `.touch_stock_pad`.
- .noinit (upstream cy_syslib cy_faultFrame) was already being dropped by --gc-sections because it is unreferenced. It is now an explicit /DISCARD/, so the link would fail if anything referenced it.
- Stack: 4212 B vs stock 4264 B.

## inventory scanner
- `FLAG(` used as a macro identifier and the phrase "not inferred" are no longer counted. All of apollo's 23 flags were the FLAG() macro in am_hal_sysctrl_sleep_variant.c.
