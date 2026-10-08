# Floating range and scaling eleven binary64 literals

Partial/unaccepted;88 exact non-code bytes483908..483960, eleven little-endian eight-byte slots after return483904..483908. Exact hexadecimal binary64 values, by address:
483908 positive infinity;
483910 -0x1.fffffffffffffp+1023 (negative maximum finite);
483918 +0x0.0p+0;
483920 0x1.34413509f79fbp-2;
483928 0x1.68a288b60c8b3p-3;
483930 0x1.287a7636f4361p-2;
483938 0x1.a934f0979a371p+1;
483940 0x1.26bb1bbb55516p+1;
483948 -0x1.62e42fefa39efp-1;
483950 0x1.a36e2eb1c432dp-14;
483958 0x1.e848000000000p+19.

All full-width reads consumed by maps21744,21746,21748. 483908 equality special fallback;483910 negative lower boundary;483918 sign comparison zero. Other constants preserve exact bits for arithmetic and thresholds, without substituting runtime logarithms or rounded decimals. Four-byte reference prefixes in previous artifacts are now supplemented by these full slots. Exact raw bytes in bytes.json authoritative. Data candidate ends483960; no executable classification inferred from disassembly of literals. No C,freeze,wholecoverage or equalityclaim.
