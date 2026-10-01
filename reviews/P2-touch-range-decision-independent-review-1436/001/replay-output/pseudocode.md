# Range decision helper at 61F0

The 48-byte body [61F0,6220) starts a boolean result from unsigned (second argument <= third argument). If mode is 2, return that result. Otherwise load a fifth argument from the incoming stack and clear the result if it is below the fourth argument. For mode zero, call A7CC(fifth argument,fourth argument); clear the result when the returned R1 remainder is nonzero. Other modes do not call division. Restore the frame and return the boolean.

The 288 original-instruction fixtures vary the comparison, mode, stack argument and controlled remainder, including a zero divisor. A7CC remains explicitly controlled; zero-divisor behavior is not inferred. Exact call arguments, result and frame are checked. Physical meanings remain unresolved. No canonical admission or C implementation.
