# Row enable at 7DDE

The 38-byte leaf [7DDE,7E04) returns zero without memory access for unsigned index greater than2. Otherwise read descriptor word+16 and row byte+35 at stride60. Return1 exactly when both bits1 and2 are set, else0. No stores,calls orstackchanges.

The1536 original-instruction fixtures exhaustall256flagbytes acrossvalidindices0/1/2 andthreeinvalidindices, checking exactreads and no writes. Pointervalidity andphysicalmeaningremainunresolved. No canonical admission or C implementation.
