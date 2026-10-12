# Native completion303fb8 audit

Direct little-endian ARC EM DSP instructions303fb8..304140, authenticated input em-inspection.bin base302400 SHA2560de6e945a56ec886a92e44d4eaefe02fbca6db11f8747876e30bffb45cffce03. All named lower calls already selected; indirect record callbacks still require exact argument/state translation.

Critical differences from convenient pseudocode:

1. LDB.AB at303fc2 reads state8015c4 before advancing captured root to8015cc.
2. State2 branch303fd4 jumps before `r0=first-3` at303fd8. Branch30405c therefore compares original incoming R0 unsigned against2. It does not compare first-3. Native state2 setsstate3 before the branch and captures incomingword+44 descriptor in delay slot.
3. State2 lower branch304060/62 loads descriptorcallback112 intoR2; laterstate2 first==0 branch304080/86 loads same callback intoR12, then stores lowR2 atdescriptor133. This is the callback address low byte, not original second argument. Descriptor136/140 and134 retain incomingthird/fourth/fifth.
4. State3 branch captures callback116 intoR2 before branch; callback0/1 argument ordering and optional120 follow-up must retain fresh callback loads.
5. Successful initializer paths replace preservedR17 (original first) with numeric8013f0; late callback arg1, request30faec incomingR0 and fallback conditions must use that changed register value.
6. Descriptor template20B3343f8 already source-selected. Stack28B contains 8B header plus20Bscratch; copied template->record30fc28->request30fcd8 and zero-scratch->record30fc28->packetrequest30faec are distinct paths.
7. Return is nativeR19 flag, initially0, set1 only aftercommonfinish3045c0. Some successful callback paths therefore return0.

Required next step: source each control path including optional/mandatory indirect calls; controlled fixtures must distinguish original inputs, callback address bytes, changedR17, and all state modes. No completion/runtime claim from this audit.
