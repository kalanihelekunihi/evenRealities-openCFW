# SPI transport loop review

The linked source and stock read/write loops both form an end pointer by
adding the original count to the original buffer address, then compare the
current pointer with that end before accessing a byte. The source C uses an
unsigned index; the current native C-SKY compiler lowers it to that same
pointer loop. This review applies to valid, nonwrapping buffers in ordinary
RAM, with no overlapping MMIO or stack-frame storage.

For such a buffer, after k completed iterations the current pointer is B+k.
The body executes precisely while k differs from N. A completed iteration
polls the appropriate readiness bit, performs one byte access and advances
the pointer by one. Starting with k=0 therefore performs exactly N accesses,
ending at B+N, provided each poll eventually observes readiness. The zero-count
path skips all buffer accesses, including when B is zero. It still performs
the stock controller setup and completion waits; the read count register
receives unsigned N-1, which is 0xffffffff for N=0.

The read instruction truncates the FIFO word to its low byte. The write
instruction zero-extends its source byte into the FIFO word. The modeled
pattern `(71*k+255) mod 256` visits all 256 byte values over 256 iterations
because 71 is odd. This is coverage of data values, not proof of hardware
behavior or arbitrary memory aliasing.

The exact MMIO addresses/order and nested call frames are checked by the
read/write decoded interpreters. Delayed readiness schedules exercise loop
repetition; no timeout has been inserted. Continued hardware non-readiness can
prevent return, as in stock. Controller-specific transfer-size restrictions,
interrupt interactions and whole-device execution remain unqualified.
