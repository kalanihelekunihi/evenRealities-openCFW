# ADC context/channel configuration: next bounded leaf

Locked original42eb74..42ebaa=54 bytes and42eaf6..42eb74=126 bytes, SHA f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5. Source `g2/components/bootloader/initializer_callbacks/adc_configuration.c/h`. [93 original/source tests](../adc-configuration-leaf.json) PASS with all180 original body bytes visited; no external-call stubs. This is a separate retained leaf ELF f65433f592e610a3139da139be3d86e76f1d29232b563c949be84968ee17937c, not the shared seven-case integration image.

Context configuration reads byte+1 and low10 bits of word+4, writing `((byte1 & 7)<<16)|(word4 & 0x3ff)` to40038040. Startup passes copied descriptor words from43402c. No argument null guard. Channel configuration validates full32-bit index<8 else5; selector word+4 must be0x20..0x3f else6. Invalid context returns2 first. Both load handle+4 before NULL/magic check. No allocator or child calls.

```c
word = ((byte0 & 7)<<24) | ((selector & 63)<<18)
     | ((byte8 & 3)<<16) | ((byte9 & 15)<<8)
     | (byte10<<1) | byte11;
MMIO[0x4003800c + 4*index] = word;
RAM[0x2002702c] = RAM[0x2002702c] + 1;
return 0;
```

Byte10/11 are not boolean-masked: larger values can set additional bits. The counter increments after register programming on every valid call, including repeated calls to the same channel, and wraps32-bit. It is not a proven unique-channel count. This is the word init/reset clear, different from temperature cache20027028. Tests cover index/error precedence, selector endpoints, field masking/unmasked enable bytes, repeated updates and wraparound, with RAM MMIO. No physical ADC, null fault, task scheduling or atomicity proof. Shared integration of these next two bodies is outstanding; do not add this leaf result to the seven-case completion numerator.

Pinned SDK5.1 register/header cross-check:40038040 is internal trigger timer configuration; byte+1 selects CLKDIV bits16..18 and word+4 supplies10-bit count. The byte+0 enable field in the SDK-style packed input is not read by this body. For slot configuration, byte0 maps measurement averaging, word4 maps tracking cycles(32..63), byte8 precision, byte9 selected input channel, byte10 window comparison, byte11 enable. Startup slot0 bytes encode128-average measurements,32 tracking cycles, precision0, external input3, window compare0, enabled1. These are register interpretations, not a proven analog sampling rate or timing measurement.
