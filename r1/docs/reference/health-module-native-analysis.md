# R1 health startup module: native contract and boundary

Subsequent [C implementation and verification](health-module-c-review.md) uses
this contract; the unresolved-route statements below describe this analysis stage.

The [REA and native-probe receipt](health-module-native-analysis.json) checks
startup module `0x4c5c4` against the locked R1 application. Its code ends immediately
after the tail branch at `0x4c606`, giving 70 executable bytes through `0x4c609`.
The former 158-byte inventory span included literals, strings and neighboring
routines. Only this row's size is corrected; it remains an unresolved source route.

The observed call sequence is:

1. Call `0x50998` with pointer `0x3d151`.
2. Read the handle at `0x20006e98` after that call. If zero, register `acc`/`algo`
   with callback pointer `0x3cd81`, rate 1 and flags 1; publish the returned word
   after registration, even if the provider itself modifies the handle.
3. Store byte 2 at `0x2001e479`.
4. Register group 4 callback `0x43789`, then group 3 callback `0x3d1b9`, each
   using the address `0x20006610` as its thread-reference argument.
5. Restore the entry frame and tail-call `0x3d0fc`; return its raw R0 word.

Thirty-six native probes cover zero/nonzero/full-word handles and registration
results, first-provider handle installation/clearing, registration-time handle
mutation, and subscriber-time state mutation. They assert call order, exact
arguments, late handle publication, byte/word write widths, adjacent memory guards,
restored stack and preserved registers. Intermediate provider return words do not
stop startup. Callback bodies are not invoked; pointer arguments alone do not
establish their callable signatures.

This is an analysis receipt for the next C implementation, not C behavior or
instruction qualification. The touched RAM cells still need ownership and native
cold-initialization checks before a production definition is introduced. No source
plan, firmware source, manifest or existing composition report changes here.
