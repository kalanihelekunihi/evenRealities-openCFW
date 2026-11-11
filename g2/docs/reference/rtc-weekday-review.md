# RTC weekday helper — compilable-C campaign

The two existing callers `DRV_RtcSetTime` and the notification list referenced
`rtc_weekday_from_date_4d3cf8`, with no definition in the registered G2 tree.
The new unit implements stock address 0x004d3cf8, not a generic calendar API.

REA/Ghidra 12.1.4 recovered the complete 204-byte function and read both twelve-word
month tables at 0x730ee4 and 0x730f14. The body SHA-256 agrees with the existing
corpus record (`f6046590f6b197308e912a8a4f1bbd45f46ef9573acd47a369829a8bd806eb0c`).
The evidence JSON records the original payload identity, mapping, provider and
analysis-wrapper identity. Only the analysis wrapper contains stock instructions;
the firmware build compiles the C unit and contains no added opcode array.

The function accepts nonnegative signed years, months 1–12 and positive signed
days. It returns 7 for invalid inputs. Critically, its leap predicate uses
`year % 100 != 0 || year % 400 != 0`; this accepts 1900/2100 leap days and rejects
2000/2400 leap days. The implementation deliberately preserves this observed
behavior, as well as uint32 wrapping and the final signed remainder.

The ephemeral harness in `build/g2-c-wave-01/compare.py` executes the stock body
and a clang-compiled Cortex-M4 C body against the same argument triples. All
12,240 cases pass, including explicit century/invalid/large-value cases and
10,000 seeded mixed input triples. This is bounded emulation evidence; neither
whole-firmware integration behavior nor physical RTC behavior has been verified.

No new upstream dependency was required. Whole-firmware completeness remains
open in `g2/docs/C-RECONSTRUCTION-PROGRESS.md`.
