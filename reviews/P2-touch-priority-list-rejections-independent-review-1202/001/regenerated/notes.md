# Priority-list rejection probes

Six original-instruction fixtures exercise null input, zero required word at input+12, zero required word at input+0, and the supplied input already present at head, middle or tail of a finite linked list. Every case returns zero and restores SP. The entire non-stack synthetic RAM region remains byte-identical; only frame stores occur. These fixtures supplement1199 without altering it.

Duplicate rejection traverses to the supplied pointer and does not reinsert it. The tests do not establish termination for cyclic lists that never contain the input, index bounds, memory validity or concurrent access. No canonical admission or C implementation.
