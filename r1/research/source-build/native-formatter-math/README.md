# Native formatter arithmetic bundle

`build_native_formatter_math.py` links recovered C decimal conversion,
unsigned conversion, addition, multiplication, restoring division, signed
shift, normalization and rounding with the existing source integer runtime.
The latter reuses pinned LLVM compiler-rt unsigned division and recovered EABI
adapters. Every source, header, provider report and object is hash-validated.
`report.json` requires no unresolved symbols in the relocatable output.

This is a decimal-arithmetic dependency bundle, not a complete formatter or
firmware image. The native parser, variadic wrapper and callback/frame effects
still require source reconstruction and complete ABI evidence. Floating-point
bit behavior follows authenticated native bodies; upstream IEEE behavior is
not substituted for exceptional or subnormal cases. Full instruction identity
and hardware operation remain separate, unproven gates.

`native-formatter-product/formatter-integration-verification.json` executes this
linked bundle in the native formatter graph. Separate direct provider and
broader decimal-chain receipts record bounded behavior checks and limitations.
