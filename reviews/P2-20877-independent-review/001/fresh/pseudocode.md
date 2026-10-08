# Selector two independent flag bit-three then two diagnostics

Partial/unaccepted;112instructionbytes;inherited40frame,R6fullhelperresult. D27Cquery43D0CEbit1zero→D2B8. Otherwiseptr=literal47D900;freshunsignedbyte[ptr]bit3→SP12;independentlyreloadbyte[ptr]bit2→SP8;literal47D95C→SP4;123→SP0;43D574(4,literal47D918,literal47D914,literal47D910,123,literal47D95C,freshBit2,earlierFreshBit3).
D2B8freshquerybit0one→D2C8;elseanotherquerybit2zero→pendingD2EC. D2C8R1=literal47D960,ptr=literal47D900;freshbytebit3→SP0;independentlyreloadbytebit2→R3;R2=R1;43CE9E(0x10800000,literal47D960,same,freshBit2,earlierFreshBit3);fallthroughpendingD2EC.
Preservefourorderedbyteobservationsacrossdiagnosticpaths; no sharedflag snapshot/stabilityassumption. ExtractedbitsUXTB0or1;writeslocalSP0..12. No C/freeze/completenessclaim.
