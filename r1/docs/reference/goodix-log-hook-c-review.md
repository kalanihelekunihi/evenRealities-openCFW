# R1 Goodix formatted log hook in C, 2026-11-10

The upstream Goodix GH3X2X demo code declares `gh3x2x_print_fmt` as a
variadic logging hook. `r1/src/application/goodix/native_goodix_logging.c`
now supplies it as C source: it formats with the existing R1
`r1_native_vsnprintf`, bounds output to 255 bytes, and calls the synchronous
R1 RTT writer on channel 0. It returns without a write for a null format or
an empty/failed format. The old pre-consolidation port forwarded only the
format string; this implementation preserves formatted arguments. This is a
source integration hook, not a stock function with bytes to compare.

The ignored host mock under `build/r1-goodix-log-probe-20261110/` verifies
integer/string formatting, empty/null suppression and long-message
truncation. The normal Arm source build compiles this exact unit among 963 R1
units, with no failures or duplicate strong symbols. The strict bootloader
link passes. The strict application link has 39 undefined references and a
29,928-byte full flash load overflow, 64 bytes above the prior checkpoint.

The host mock does not validate the Arm formatter's output, RTT hardware or
physical Goodix log behavior. The source formatter and RTT writer are separate
compiled units already present in the R1 manifest.
