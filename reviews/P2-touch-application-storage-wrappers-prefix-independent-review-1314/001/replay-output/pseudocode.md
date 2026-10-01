# Application prefix with original storage wrappers and delay

Actual 34D8,3520,35B0 and3568 execute under 395C. Their deeper storage calls 8A38,8A78,8AE0 and8AAC remain controlled with zero status and no memory mutation. Initialization sets its ready flag, all wrappers pass the original context arguments, and 395C constructs expected magic/default object on the supplied zero state.

Actual A2F0 executes its original RAM-derived delay calculation and calls actual 4480, without a delay substitution. The fixture increases instruction cap to accommodate this loop and still reaches 3D50. Six later application dependencies remain controlled. All previous original clock, SysTick, register, descriptor and callback checks remain. Synthetic external clock tables, deeper storage behavior, physical timing and later application semantics remain unresolved. No canonical admission or C implementation.
