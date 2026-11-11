# Main unsigned division support (retired)

`division_support.c` used to hold a hand copy of the stock IAR
`__aeabi_uldivmod` (0x47cc60). All of its callers are compiler-generated, so
the final link takes `__aeabi_uldivmod` from libgcc (`-lgcc`) instead; the
unit is empty and listed for removal. Zero divisor: stock returned the
numerator with a zero remainder, libgcc returns all-ones (zero for a zero
numerator) and calls `__aeabi_ldiv0`; the only caller that can pass a zero
divisor (the buzzer period) now guards it in C and keeps the stock value.
