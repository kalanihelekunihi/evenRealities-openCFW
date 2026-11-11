# R1 64-bit division caller closure, 2026-11-11

The R1 application now has no `__aeabi_uldivmod` or `__aeabi_ldivmod`
references or definitions in any compiled R1 unit. The two handwritten EABI
register adapters have been removed from `r1/src/application/runtime/integer_eabi.c`.
The source-owned `r1_runtime_udivmod` and `r1_runtime_sdivmod` C helpers remain.
They expose quotient return and an optional remainder pointer through normal
C calling conventions; `integer_eabi.h` declares the interface.

## Why the call sites changed

The initial source report had eight linked unsigned and five linked signed
EABI caller objects. Four health-record mergers and the local-calendar and
daily-metadata functions consumed the remainder in R2. They now call the C
helpers directly with a remainder pointer. The local Goodix NADT classifier
and mean update call the signed helper for quotient-only division. GoMore's
piecewise clamp now uses 32-bit C division after explicitly wrapping its
subtraction and multiplication to 32 bits.

Pinned upstream and vendor source is copied through the existing manifest
`generated` mechanism, with exact one-match substitutions. The generated
nrfx WDT copy calls the unsigned C helper for its reload conversion. The
Goodix AGC copy calls the signed C helper for both 64-bit quotients. Its
second numerator is a signed `GS64` accumulator, so this also covers negative
accumulated values. Both Newlib `vfprintf` variants use one C helper call per decimal
digit to obtain quotient and remainder. The pinned originals are unchanged.
The unlinked R1 time-calendar candidate also uses the signed helper, leaving
zero EABI divmod imports across all 1,045 R1 units.

`build/sources-r1-eabi-pure-c-20261111/report.json` compiles 963/963
application and 82/82 bootloader units with zero failures or duplicate strong
symbols. Strict application and bootloader links pass with zero undefined
symbols and zero archive members. The application image is 694,196 bytes,
SHA-256 `78850954ba67cb308869aa8f3b823c8a2f33bc1d1f35db4eb2435acaceb06eba`;
the bootloader image remains 23,024 bytes, SHA-256
`08e108776638ad4feaf2eada3861ab37d587b44ae3b5b75daacfa386ea67ac67`.
The application image is byte-identical to the immediately preceding link,
where the EABI adapter sections had already been garbage-collected. Future
64-bit division expressions that reintroduce an EABI divmod call will fail
the strict link until converted or given a complete ABI implementation.

## Executed behavior checks

- The four changed health-record mergers pass 400 activity, 500 HR, 600 HRV
  and 600 SpO2 paired stock/C cases with modeled FlashDB, calendar and log
  providers. The local-calendar function passes 2,896 pairs. The changed
  day-start function passes 84 pairs. Receipts are under ignored
  `build/r1-eabi-callers-replay-20261111/` and
  `build/r1-eabi-callers-daily-20261111/`.
- The Goodix NADT source ELF passes 32 fresh-input sessions of 100 samples
  against stock, comparing state, output, workspace and per-call trace. The
  corrected GoMore clamp passes 920 paired int32 inputs. Its predecessor
  differed on 278 of those 920 inputs because it missed stock 32-bit wrapping
  and signed-16 narrowing. Receipts are under ignored
  `build/r1-eabi-local-replay-20261111/`.
- The current linked C helper entries pass 1,862 unsigned and signed
  quotient/remainder pairs against an independent Python integer oracle,
  including zero denominators, signed extremes, day/decimal divisors and
  random full-width inputs. This is a Cortex-M4 Unicorn execution of the
  final application ELF; the receipt is `divmod-helpers.json` in the same
  ignored replay directory.

The generated WDT, AGC and Newlib substitutions preserve the original
arithmetic operand types and have passed source compilation and strict
linking. An audit corrected an unsigned AGC helper selection for the signed
accumulator path. The corrected strict application image is 694,196 bytes,
SHA-256 `6ca24db9ec3209c9abd20858fede662b368f84ea8be5bb0cfb698b6b9f405068`;
the bootloader remains unchanged. The new receipts are under
`build/sources-r1-eabi-agc-signed-20261111/`,
`build/r1-link-eabi-agc-signed-20261111/`, and
`build/r1-boot-link-eabi-agc-signed-20261111/`. The corrected final ELF also
passes all 1,862 helper pairs; its ignored receipt is
`build/r1-eabi-local-replay-20261111/divmod-helpers-agc-signed.json`. The
generated substitutions have not received complete provider-level or hardware
replays.
The health and calendar fixtures model external providers; the NADT replay
uses Unicorn rather than a physical R1.

A direct C aggregate return cannot serve as a drop-in EABI divmod entry under
the current Clang. A probe under ignored `build/r1-eabi-aggregate-c-20261111/`
shows the compiler passes a hidden result pointer in R0, rather than returning
quotient in R0:R1 and remainder in R2:R3. An earlier `value_in_regs` attribute
probe was rejected by Clang. Removing every caller avoids introducing a
partial EABI implementation.

A volatile-zero C divisor probe under ignored
`build/r1-divzero-c-probe-20261111/` emits `UDIV`, but the expression has
undefined C behavior at zero. The architectural zero-divisor primitive
therefore remains a separate assembly boundary.
