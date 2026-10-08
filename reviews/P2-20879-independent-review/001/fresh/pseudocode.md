# Selector two independent flag bit-five then four diagnostics

Partial/unaccepted;112instructionbytes;inherited40frame,R6fullhelperresult. D2ECquery43D0CEbit1zero→D328. Otherwiseptr=literal47D900;freshunsignedbyte[ptr]bit5→SP12;independentlyreloadbyte[ptr]bit4→SP8;literal47D964→SP4;124→SP0;43D574(4,literal47D918,literal47D914,literal47D910,124,literal47D964,freshBit4,earlierFreshBit5).
D328freshquerybit0one→D338;elseanotherquerybit2zero→pendingD35C. D338R1=literal47D968,ptr=literal47D900;freshbytebit5→SP0;independentlyreloadbytebit4→R3;R2=R1;43CE9E(0x10800000,literal47D968,same,freshBit4,earlierFreshBit5);fallthroughpendingD35C.
Preservefourorderedbyteobservationsacrossdiagnosticpaths; no sharedflag snapshot/stabilityassumption. ExtractedbitsUXTB0or1;writeslocalSP0..12. No C/freeze/completenessclaim.
