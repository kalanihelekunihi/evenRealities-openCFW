# R1 GoMore numerical sleep score in C, 2026-11-10

`r1/src/application/runtime/native_gomore_sleep_score.c` now binds stock
`0x6778c` to `gomore_primitives_sleep_score`, using the source-built native
double `tanh` and float `powf` providers. The input is the existing 19-float
statistics record; the hard-float result returns in S0. This closes
`r1_gomore_sleep_score_native` in the application link.

Paired Unicorn execution of the locked application and source-linked score
passes **1,181 cases** with exact S0 bits and provider-call arguments. Cases
cover duration and weight boundaries, zero and varied wake periods, an
11-by-11 REM/deep weight grid and 1,024 deterministic finite random records.
Both runs use the same modeled tanh/powf results; the stock run executes its
own arithmetic helpers while the source run links the normal source-owned
compiler runtime. The probe is under ignored
`build/r1-gomore-sleep-score-probe-20261110/`. Its compiled
`gomore_primitives.c.o` has SHA-256
`46a19f4231672f56d656219e32cc812d7c37cd6d17167118463a6300ba234196`,
identical to the authoritative 960-unit build object.

The comparison exposed four details corrected in the shared C primitive:
stock rounds the REM/deep weights together before adding the wake term;
recomputes the wake ratio from rounded percentage; selects 0.4 versus 0.3
in the opposite branch from the prior implementation; and multiplies the
duration score by a rounded reciprocal instead of dividing directly. The
initial candidate disagreed on 196 of 292 cases, including low-bit errors.
The corrected implementation has zero mismatches in the expanded set.

The strict bootloader link passes. The application now has 42 undefined
references and a 29,768-byte full flash load overflow, 1,528 bytes more
than before this unit. The paired test does not cover nonfinite statistics,
real tanh/powf implementations, physical sleep data or board execution.
