# Touch buffer configuration adapters

9AD8..9AF0 is 24 instruction bytes. A nonzero length with null buffer reaches BKPT9AEC before stores. Otherwise store buffer at context+28, length at+2C, zero at+30 and+34, return through LR preserving incoming R0. 9AF0..9B06 is22 instruction bytes: same guard at9B02, store buffer at+38,length at+3C,zero at+40. Both allow null buffer when length is zero. No context-pointer guard, stack frame or interrupt masking occurs. The following9B06 routine is excluded.

Sixteen original-instruction fixtures cover both adapters, null/nonnull buffers and four lengths, checking exact stores, guard stop and R0 preservation. Breakpoint continuation, invalid context pointers, buffer use and concurrent access remain unresolved. No canonical admission or C implementation.
