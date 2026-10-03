# Independent review 2243

**Result:** PASS_SCOPED.

The source, body `[0x51BC,0x52B6)`, literal `[0x52B8,0x52BC)`, and all candidate file hashes match the receipt. The literal is `0x0FFF0000`. Decoded control flow supports the row/parameter calculations, the first destination word’s preserved bits and masked count field, the bypass bit-12 path, and the secondary selection condition `validity == 1 && row.byte58 <= group`. The selected bytes and item byte are ORed into the second word in the documented positions; the body writes the two destination words in order, returns zero, and restores R4–R8/SP.

An isolated replay regenerated all 648 fixtures. It asserts the exact ordered writes, both final words, zero return, and preserved registers. The group values 0/1/2 straddle the fixed row-byte-58 threshold of 1; count values 0/1/65535 cover the zero, minimum nonzero, and upper boundary; both bypass states and six validity values are represented.

**Fixture limitation:** Configuration bytes 90, 91, and 92 are initialized to the same enable value in every fixture. The disassembly confirms the validity-dependent selection of those offsets, but the replay cannot distinguish a mistaken choice among the three offsets by value. Independent per-byte patterns would close that behavioral gap. Source fields otherwise use only all-zero or one fixed nonzero pattern, so broad independent field-value coverage is also absent.

**Scope:** Invalid pointers, aliasing, and physical field meanings remain unresolved. No canonical admission is made.
