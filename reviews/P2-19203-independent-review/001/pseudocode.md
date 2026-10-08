# Three object updates and epilogue 0x46A64A..0x46A6D2

Partial/unaccepted;136instructionbytes. Inherit48frame,R4=addressliteral46ACD4,R5=addressliteral46AE98 and flagsfromfreshword[R5]comparedzero. Ifzero call44104C(0x00FFFFFF,live1..3),elsenonzero call44104C(literal46B020,live1..3). ForwardFULLchildR0asR1, R2=0,R0SECONDfreshword[R4] ->44140E(liveR3). Priorfirstobject-null route skips to668.

R4=addressliteral46ACD8;freshword[R4]zero skips696. Nonzero freshword[R5]FULL1 selects44104C(0x00FFFFFF),else44104C(literal46B020);both forwardFULLchildR0toR1,R2=0,R0SECONDfreshword[R4] ->44140E(liveR3).

R4=addressliteral46B010;freshword[R4]zero exits6CC withR0zero. Nonzero freshword[addressliteral46B00C]FULLnot3 exits withthatR0. FULL3: freshword[R5]FULL2 selects44104C(0x00FFFFFF),else44104C(literal46B020);forwardFULLchildR0asR1,R2=0,R0SECONDfreshword[R4] ->44140E(liveR3). Shared6CC ADDSP20 thenLDMIA4/5/6/7/8/9/PC28 returnsliveR0. Initialguard route also reachesitwithzero. Do not assume normalization or childcontracts. No C/freeze/corpusclaim.
