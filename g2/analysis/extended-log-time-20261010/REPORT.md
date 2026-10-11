# Fixed logger timestamp formatting

The logger calls stock `0x44b728` with capacity 5, the image literal `"%ld"` at `0x43da6c`, and a 32-bit tick value. `time.c` source-defines precisely that call shape: signed decimal characters, at most four visible bytes plus NUL, and the full would-have-been decimal length. It does not implement general `snprintf`.

The image is the official G2 2.2.6.10 OTA stripped 32 bytes and mapped at `0x438000`, SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. `verify.py` compiles M55 and M4 with warnings as errors and executes **194** original/source Unicorn comparisons, including zero, decimal boundaries, signed extremes and seeded random values. Return, 32-byte destination window and stack restoration agree. This closes the logger's fixed timestamp call, not the general formatter at `0x44b76c`.
