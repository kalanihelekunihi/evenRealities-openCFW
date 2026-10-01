# Highest-bit scale helper at 6220

Start result at 65535 and mask at 32768. While result is greater than 1 and input does not contain the current mask bit, shift result and mask right once. Return result. For a halfword input with highest set bit k, return (1 << (k+1)) - 1; zero and one both return 1. Higher input bits are ignored because the tested mask begins at bit 15.

The code span is [6220,6238), 24 bytes, followed by the 65535 literal at 6238. All 65536 halfword inputs execute the original instructions and agree with an independent bit-length model. The compact result vector is retained with its hash. This helper has no calls, stores or stack operations. Physical meaning remains unresolved. No canonical admission or C implementation.
