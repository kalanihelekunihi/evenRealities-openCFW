# Touch settings initializer 395C

Body 395C..39F8 is 156 instruction bytes, excluding its following literal pool. Call 34D8; nonzero status prints through actual zero-return 3EE0 and returns. Otherwise call 3520(0,200009D0,8). If read succeeds and the first word equals 45564E55, retain existing halfwords at offsets four/six, except replace a zero timeout at six with 1000. Print their values and return zero through 3EE0.

A failed read or mismatched magic prints and calls 35B0. On erase failure print and return zero. Otherwise call A2F0(10), set word magic 45564E55, halfword offset four zero, halfword offset six 1000, then call 3568(0,200009D0,8). Both write success and failure print and return zero. Original 3EE0 executes; five deeper helpers are controlled status boundaries. The procedure restores its frame on each branch.

Sixty-four original-instruction fixtures cover six binary preconditions/statuses, checking reached control sequence, read/write arguments, exact local object stores, return and frame. Controlled storage routines do not mutate memory; supplied object states are explicit. Storage functionality, physical delay and diagnostic output remain unresolved. No canonical admission or C implementation.
