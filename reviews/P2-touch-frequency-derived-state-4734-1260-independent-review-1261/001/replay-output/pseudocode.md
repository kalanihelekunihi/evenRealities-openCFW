# Touch frequency-derived state4734

Actual4734 calls46F8. A zero rawresult returnszero with no derived-state writes. NonzeroF storesF at20000878, then executes actualA6C0 unsigneddivision on(F-1,1000000), addsone and writes only thelowbyte at20000870. It executes actualA6C0 on(F-1,1000), addsone, stores theword at20000874, shifts thatwordleft15 modulo2^32 andstores at2000086C. The shiftedvalue is rawR0 on return; R4 andeightbyteframe restore.

Ten original-instruction fixtures replace only46F8 and execute both divisions. Independent integerceil postconditions check boundaryfrequencies, byte truncation and wordoverflow. Frequency source andphysicaltiming meanings remain unresolved; syntheticRAMtests do not validatehardware clocks. A6C0's general behavior outside these pairs remains separate. Body4734..476A excludesNOP/pool. No canonical admission orCimplementation.
