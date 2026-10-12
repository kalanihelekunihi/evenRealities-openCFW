# IMCRA block scale and peak-shift source evidence

Native image-B SHA256
`d23fb40126b434e3c47a605997d25210a3cb80302bad7d6c302aaf790627a941`,
base `0x10003000`.

- `0x1000e28c..0x1000e2c3` loops over `count` signed halfwords. Positive
  shift uses `asr`; nonpositive shift negates the count and uses `lsl`.
  `stbi.h` stores the low halfword and advances by two. The source's
  negative-shift cast preserves modulo-16-bit storage. Actual connected
  shifts are expected within the halfword normalization domain; arbitrary
  signed 32-bit shift counts are not qualified.
- `0x1000e2c4..0x1000e313` reads the first signed halfword before its
  `count>1` branch, takes signed absolute values (including 32768 for
  -32768), applies `max.s32`, and scans bits from `0x80000000` downward.
  A nonzero peak at bit `b` returns `b-14`; zero returns `-15`. This
  corrects the Ghidra decompilation's DSP stub and broken loop.
- `verify_imcra_block_scale_host.c` checks nine native-branch fixtures,
  including `-32768`, all-zero, multi-element peak, right arithmetic shift,
  and left truncation. 9/9 pass. This is a bounded source/ISA check;
  physical signal-path timing remains unqualified.

Target compile/link: `build-imcra-block-round/receipt.json`, 130/130 C-SKY
units and `ld -r` PASS; linked SHA256
`b60b2d601c114b7f6249fe026a118a23ca1c74198422475880ee716725139a62`.
Four genuine imports remain: `__fe_getround`, `__fe_raise_inexact`,
`gx8002_image_b_native_word_at_zero_1000ada6`, and
`gx8002_image_b_uart_dma_ambient_direction_100040e8`. The larger
IMCRA constructor at `0x1000e784` and `0x1000ea74` child need native
hard-float/stack argument recovery; Ghidra pseudo has bogus repeated writes
and ambient stack inputs. This is an identified source frontier, not a
product default or external hardware import.
