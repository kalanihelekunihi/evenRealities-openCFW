# Product CAPSENSE configuration source lead

Infineon's [ModusToolbox code-generation documentation](https://documentation.infineon.com/modustoolbox/docs/tem1711738698564) states that `cycfg_capsense.c/.h` and related definitions are generated from the application's own `.cycapsense` configuration. That makes example-generated files useful for ABI and schema comparison, not evidence of the G2 product's initialized tables.

The retained 45-unit touch archive and third-party source scan found no G2 product `.cycapsense`, `cycfg_capsense.c`, or `cycfg_capsense.h`. A targeted public search for those filenames with Even Realities/G2 also found no attributable product source. There is no newly identified product repository to download or register as a submodule in this pass. The 939 unowned reset-copy bytes remain a field-level reconstruction or authenticated-source-acquisition problem.
