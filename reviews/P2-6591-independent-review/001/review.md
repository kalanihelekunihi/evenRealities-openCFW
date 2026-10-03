# Independent review 6591/002

Disposition: **PASS_SCOPED**; `accepted:false`. Revision 002 is the reviewed packet; revision 001 remains preserved. I recomputed the layered evidence masks using all pinned latest instruction and word ledgers, the three candidate-extent record files, the CRC table words, and the printable-string candidates. Counts match exactly: 103,036 bytes with instruction observations, 3,104 PC-relative literal bytes, 3,212 candidate-table-extent bytes, 11,696 printable-string candidate bytes, 27,551 bytes with no represented layer, and zero overlap between layers 1 and 2. All 924 interval records and hashes match.

The bit layers mean only their stated evidence kinds. In particular, printable strings are not proven data, candidate extents are not admission, and zero instruction/literal overlap does not prove code/data ownership. Gaps may be covered by other schemas. No canonical files or gates changed.
