# Source formatter engine

`build_native_formatter_engine.py` links the recovered main parser, source
arithmetic bundle and C output helpers with no undefined symbols. Each provider
report, source/header input and object is hash-validated. Compiled source owns
56 bytes of native parser tables/sign literals and the arithmetic zero literal.

The native/C direct parser test passes 39,002 cases, including 303,233 callback
observations, 10 matching faults, every flag subset, integer modifiers, dynamic
precision, aligned 64-bit arguments, `%n` writes and four callback mutation
modes. An initial signed-byte translation error is retained as a counterexample;
the final source passes unsigned byte callback regressions. The 225-case native
snprintf-wrapper graph executes this actual linked engine and matches outputs.

This is not a complete source firmware or byte-identical formatter proof.
Variadic wrappers remain native in the graph. Complete caller-saved/flag ABI,
original native136-byte private frame and arbitrary alias identity, full input
domain, instruction identity and hardware behavior remain explicit gates.
