# SMP string comparator

`compare.c` reconstructs the complete stock function at 0x44b610..0x44b63a as an SMP provider callback. The C accepts the handler's opaque context and two 32-bit pointer words, compares at most `length` bytes, stops on equal NUL, and returns 0, 1 or UINT32_MAX with the stock unsigned ordering. It reads no bytes for length zero. The pointer words are firmware RAM/data addresses; host code must map them before calling the ARM candidate.

The authenticated 42-byte body and the SDK string comparison semantics bound this source. `g2/analysis/smp-provider-candidate-20261010/verify.py` checks 500 original-versus-C comparisons. No logging, queue, CCB, allocator or state-machine dependency is claimed by this unit.
