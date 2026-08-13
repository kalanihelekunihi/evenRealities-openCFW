# Toolchain runtime correlation

The stock application retains standard C and Arm EABI helpers near its vector/startup region.
These functions are provider code supplied by the compiler runtime. Production must link the
selected Arm runtime implementation rather than recreate them from decompilation.

| Stock entry | Runtime symbol | Function-local discriminator |
| --- | --- | --- |
| `0x000274E8` | `__aeabi_uldivmod` | 64-step unsigned division returning quotient and remainder in `r0:r3` |
| `0x0002754A` | `__aeabi_ldivmod` | signed-magnitude wrapper around unsigned 64-bit quotient/remainder division |
| `0x000275AC` | `__aeabi_llsl` | 64-bit logical left shift in the EABI register-pair convention |
| `0x000275CA` | `__aeabi_llsr` | 64-bit logical right shift in the EABI register-pair convention |
| `0x000275F4` | `isspace` | locale ctype-table lookup and whitespace-class bit test |
| `0x00027606` | `qsort` | recursive partition, comparator callback, and bytewise element swap |
| `0x000276A4` | `rand` | `seed = seed * 1103515245 + 12345`, returning `seed >> 1` |
| `0x000276B8` | `srand` | writes the runtime PRNG continuation state |
| `0x000276C8` | `gmtime` | UTC second/minute/hour/weekday/year/day/month expansion into static `tm` storage |
| `0x0002775C` | `memmove` | aligned forward copy when non-overlapping; bytewise reverse copy on overlap |
| `0x0002779C` | `__aeabi_memset` | `(destination, length, byte)` fill convention |
| `0x000277AA` | `__aeabi_memclr` | two-argument zero-fill thunk |
| `0x000277AE` | `memset` | standard argument reorder into the EABI fill helper and destination return |
| `0x000277C0` | `strcat` | find destination NUL, then copy source through its terminator |
| `0x000277D8` | `strncpy` | fixed-count copy with NUL padding |
| `0x000277F0` | `strlen` | terminator scan and pointer-difference result |
| `0x000277FE` | `strcmp` | unsigned-byte comparison through mismatch or NUL |
| `0x0002781A` | `memcmp` | bounded byte comparison loop |
| `0x00027834` | `strncmp` | bounded string comparison with terminator stop |
| `0x00027854` | `strtok` | saved continuation pointer and delimiter-set scanning |
| `0x00027898` | `sscanf` | variadic wrapper over a string-backed scan descriptor |
| `0x00027AFC` | `__aeabi_dadd` | binary64 exponent alignment, signed significand addition, normalization |
| `0x00027C3E` | `__aeabi_dsub` | negate the second binary64 operand and tail-call double addition |
| `0x00027C44` | `__aeabi_drsub` | negate the first binary64 operand and tail-call double addition |
| `0x00027C4A` | `__aeabi_dmul` | binary64 significand multiplication, exponent/sign composition, rounding |
| `0x00027D2E` | `__aeabi_ddiv` | binary64 restoring division, exponent/sign composition, rounding |
| `0x00027E0C` | `__aeabi_l2f` | signed 64-bit magnitude normalization and binary32 rounding |
| `0x00027E38` | `__aeabi_i2d` | signed 32-bit magnitude/sign conversion to binary64 |
| `0x00027E5A` | `__aeabi_ui2d` | unsigned 32-bit conversion to binary64 |
| `0x00027E74` | `__aeabi_d2iz` | binary64 exponent extraction, truncation, and sign application |
| `0x00027EB2` | `__aeabi_d2uiz` | binary64 exponent extraction and unsigned truncation |
| `0x00027EE4` | `__aeabi_f2d` | binary32 sign/exponent/fraction expansion to binary64 |
| `0x00027F0C` | `__aeabi_cdrcmple` | reverse-order binary64 comparison with APSR flag result |
| `0x00027F3C` | `__aeabi_cdcmple` | forward-order binary64 comparison with APSR flag result |
| `0x00027F6C` | `__aeabi_d2f` | binary64 contraction to binary32 with round-to-even helper |
| `0x00027FA4` | `__aeabi_uidiv` | 32-step unsigned restoring division |
| `0x00027FD0` | `__aeabi_lasr` | signed 64-bit arithmetic shift-right result in `r0:r1` |
| `0x00028334` | `__aeabi_d2ulz` | binary64 exponent/mantissa truncation to unsigned 64-bit `r0:r1` |
| `0x000283A0` | `__scatterload` | iterate linker region records and invoke each copy/decompression handler |
| `0x000286F4` | `__scatterload_decompress` | Arm scatter-loading literal/back-reference/zero-run decoder |
| `0x00038060` | `printf` | variadic wrapper selecting the retained stdout character callback and stream context |
| `0x00038080` | `snprintf` | bounded destination descriptor, variadic scan, and conditional NUL termination |
| `0x000380B4` | `sprintf` | unbounded destination callback followed by terminal NUL emission |
| `0x000380DC` | `vsnprintf` | caller-supplied argument cursor with bounded destination and terminal NUL handling |
| `0x000381F0` | `atan` | four-region binary64 argument reduction, rational kernel, and signed `pi/2` infinity limit |
| `0x000384C8` | `atan2f` | two-argument quadrant/special-value reduction with signed-zero and infinity cases |
| `0x00038774` | `atanf` | binary32 reciprocal/half-angle reduction and signed `pi/2` limit |
| `0x000388D8` | `ceil` | positive fractional increment followed by binary64 fraction-mask clearing |
| `0x000389F0` | `ceilf` | binary32 counterpart preserving negative zero |
| `0x00038A5C` | `cosf` | quadrant reduction selecting even cosine or odd sine kernels; tiny finite input returns one |
| `0x00038BB0` | `exp` | binary64 `ln(2)` reduction, polynomial reconstruction, and exponent scaling |
| `0x00038F08` | `expf` | binary32 range reduction by `ln(2)/4`, four-way table reconstruction, and overflow/underflow handling |
| `0x000390F0` | `fabs` | clear the binary64 sign bit while preserving the remaining payload |
| `0x00039108` | `floor` | binary64 exponent split, negative fractional decrement, and fraction-mask clearing |
| `0x00039220` | `floorf` | binary32 exponent split, negative fractional decrement, and fraction-mask clearing |
| `0x00039290` | `fmaxf` | comparison-helper selection with finite/NaN second-operand handling |
| `0x000392D8` | `fminf` | inverse comparison-helper selection with finite/NaN second-operand handling |
| `0x00039320` | `log` | binary64 mantissa/exponent reduction using split `ln(2)` constants and domain/pole handling |
| `0x000396E4` | `log10f` | table-assisted binary32 logarithm with split base-10 coefficients and domain/pole handling |
| `0x00039864` | `logf` | table-assisted binary32 natural logarithm with exponent reduction and domain/pole handling |
| `0x000399D0` | `pow` | binary64 base/exponent classification, logarithmic reduction, exponential reconstruction, and integer-parity sign logic |
| `0x0003A620` | `powf` | binary32 base/exponent classification, logarithmic reduction, exponential reconstruction, and integer-parity sign logic |
| `0x0003AC88` | `round` | binary64 nearest-even integral helper plus halfway correction to away-from-zero semantics |
| `0x0003AD68` | `roundf` | binary32 nearest-even integral helper plus halfway correction to away-from-zero semantics |
| `0x0003AE04` | `sinf` | quadrant reduction with odd sine/even cosine kernels and signed exceptional handling |
| `0x0003AF94` | `sqrt` | binary64 square-root core plus finite-input range-error reporting |
| `0x0003B00E` | `sqrtf` | hardware binary32 square root plus finite-input range-error reporting |
| `0x0003B048` | `tanf` | quadrant reduction selecting tangent or negative reciprocal kernels |
| `0x0003B1C8` | `tanh` | binary64 small-input identity, `expm1` reduction, saturation, and sign restoration |
| `0x0003B328` | `tanhf` | small-input identity, rational kernel, and `expf(2*abs(x))` saturation path |
| `0x0003B5C0` | `expm1` | binary64 range reduction and compensated reconstruction of `exp(x)-1` |

## Private runtime internals

The following entries have proven provider ownership and complete functional roles, but their
private Arm-library symbol spellings are not stable ABI. The `internal:` labels are descriptive;
they are not reconstructed original names.

| Stock entry | Descriptive role | Function-local discriminator |
| --- | --- | --- |
| `0x000275EC` | `internal:ctype_table_pointer_get` | returns the active runtime locale's ctype-table pointer cell; callers dereference it before class tests |
| `0x000278D0` | `internal:scanf_integer_conversion` | sign/base prefixes, bounded digit accumulation, width and destination-size flags |
| `0x00027A1C` | `internal:scanf_string_conversion` | whitespace/bitmap selection and width-bounded destination writes |
| `0x00027FF4` | `internal:scanf_digit_value` | decimal/hex digit folding with base rejection |
| `0x00028010` | `internal:scanf_format_getc` | format cursor advance callback |
| `0x0002801C` | `internal:vsscanf_descriptor_init` | installs string input and format callbacks before entering the scan core |
| `0x00028038` | `internal:sscanf_input_getc` | bounded string cursor read and EOF state |
| `0x00028056` | `internal:sscanf_input_ungetc` | cursor rollback with base/error guards |
| `0x00028078` | `internal:binary32_round_to_even` | sticky-bit increment and tie-to-even correction |
| `0x0002808A` | `internal:binary32_pack_from_u64` | leading-zero normalization, exponent construction, sticky-bit rounding |
| `0x000280E6` | `internal:binary32_round_to_integral_even` | exponent-range split, exact-half tie handling, and fractional-bit clearing |
| `0x00028122` | `internal:binary64_round_to_even` | guard/sticky increment and tie-to-even correction |
| `0x00028140` | `internal:binary64_pack` | significand normalization, exponent/sign assembly, underflow handling |
| `0x000281DC` | `internal:binary64_scale_pow2_flush_underflow` | signed exponent adjustment with zero result when the adjusted exponent is non-positive |
| `0x0002820A` | `internal:binary64_sqrt` | 53-round restoring square-root loop followed by binary64 tie-to-even packing |
| `0x000282AC` | `internal:binary64_round_to_integral_even` | sub-half zeroing, exact-half tie-to-even, and rounded fractional-bit removal |
| `0x00028364` | `internal:binary32_compare_flags` | sign-aware monotonic bit transform and APSR comparison-flag synthesis |
| `0x0002839A` | `internal:floating_environment_control_stub` | zero-return control hook used to save and restore mask bits around a runtime math operation |
| `0x000283C4` | `internal:scanf_core` | full width/length/specifier parser and assignment accounting |
| `0x00038110` | `internal:binary64_classify` | zero/subnormal/normal/infinite/NaN bit classification consumed only by runtime math paths |
| `0x00038140` | `internal:binary32_classify` | binary32 counterpart with the same runtime category encoding |
| `0x0003F530` | `internal:printf_binary64_decimal_conversion` | power-of-ten scaling, digit extraction, precision-mode adjustment, and decimal exponent result |
| `0x00043080` | `internal:printf_core` | complete `%` flag/width/precision/length parser with integer, string, pointer, and floating conversions |
| `0x00043734` | `internal:printf_left_padding` | conditional trailing-space callback loop |
| `0x00043758` | `internal:printf_width_padding` | conditional leading zero/space callback loop |
| `0x00043BBC` | `internal:printf_bounded_buffer_putc` | writes one byte only while destination capacity remains, then advances/decrements the descriptor |
| `0x00044A6C` | `internal:printf_buffer_putc` | unbounded single-byte destination write and cursor advance |
| `0x0006570A` | `internal:printf_stdout_putc_adapter` | one-byte stdout write wrapper around the platform stream syscall boundary |
| `0x0003B40C` | `internal:binary64_polynomial_evaluate` | degree-specialized Horner evaluation through the binary64 EABI helpers |
| `0x0003B508` | `internal:binary64_positive_infinity_raise_divzero` | evaluates a binary64 one divided by zero for the runtime pole path |
| `0x0003B538` | `internal:binary64_self_add` | propagates a binary64 exceptional operand by adding it to itself |
| `0x0003B54C` | `internal:binary64_add_pair` | propagates a binary64 exceptional pair through addition |
| `0x0003B560` | `internal:binary64_invalid_zero_div_zero` | evaluates binary64 zero divided by zero for a quiet-NaN invalid path |
| `0x0003B580` | `internal:binary64_overflow_raise_square` | squares a huge binary64 constant to raise overflow |
| `0x0003B5A0` | `internal:binary64_underflow_raise_square` | squares a tiny binary64 constant to raise underflow |
| `0x0003BAB4` | `internal:binary32_positive_infinity_raise_divzero` | evaluates binary32 one divided by zero for a pole path |
| `0x0003BAC8` | `internal:binary32_self_add` | propagates a binary32 exceptional operand by adding it to itself |
| `0x0003BACE` | `internal:binary32_add_pair` | propagates a binary32 exceptional pair through addition |
| `0x0003BAD4` | `internal:binary32_invalid_zero_div_zero` | evaluates binary32 zero divided by zero for a quiet-NaN invalid path |
| `0x0003BAE4` | `internal:binary32_overflow_raise_square` | squares a huge binary32 constant to raise overflow |
| `0x0003BAF4` | `internal:binary32_underflow_raise_square` | squares a tiny binary32 constant to raise underflow |
| `0x0003BB04` | `internal:binary32_trig_argument_reduce` | table-assisted high-precision reduction to a quadrant and small residual |
| `0x0003BC9C` | `internal:errno_set` | stores the runtime math error code in the active errno cell |

Ghidra's inventory omits `0x00028010`, `0x00028038`, `0x00028056`, `0x0002808A`, `0x000283C4`,
`0x0003B538`, `0x0003B54C`, `0x0003B560`, `0x0003BAC8`, `0x0003BACE`, `0x0003BAD4`, and
`0x00043BBC` even though
their entry instructions and direct branch callers are present. They are explicit
`manual_provenance_supplement` rows. In particular, `0x000283C4` prevents the malformed recovered
end for `0x000283A0` from hiding the scan core behind `__scatterload`; the six math supplements
preserve exceptional-value tail helpers hidden by similarly overstated neighboring extents. The
bounded printf callback at `0x00043BBC` is likewise present as a literal callback pointer and a
complete disassembly body despite being absent from the recovered function list.

The ledger records `use_toolchain_runtime`; it does not assert that the current GNU runtime emits
byte-identical code to the stock compiler. Functional recompilation requires the standardized
semantics, while exact stock compiler identification and the remaining math-core and formatting
helpers remain under investigation.

The recovered `rand` recurrence is a behavioral compatibility constraint because ISO C does not
standardize a PRNG sequence. A replacement runtime must provide that sequence where stock call
sites depend on deterministic output, or the clean-room integration must select an independently
licensed provider offering it; copying the recovered routine into local source is not permitted.
