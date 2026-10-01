# Independent review 1789: scoped pass

The six bodies independently match their declared extents: 4780..4784, 4784..4788, 4788..478C, 478C..4790, 4790..47AA and 47AA..47AE. Disassembly confirms constant leaves 1, 128, 128, 0 and 0, plus the 4790 unsigned range check: zero R1 fails; otherwise R1 is replaced by 32-bit wrapped R1+R2 and compared <= 65536. All 150 isolated fixtures match returns, LR stop and unchanged SP.

The range test does not establish physical access. No canonical acceptance or coverage change is made.
