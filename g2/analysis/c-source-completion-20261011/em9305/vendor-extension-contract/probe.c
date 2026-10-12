__asm__(
".extInstruction log2p0,7,1,SUFFIX_NONE,SYNTAX_2OP\n"
".extInstruction bswp8,7,14,SUFFIX_NONE,SYNTAX_2OP\n"
".text\n"
".global extension_probe\n"
"extension_probe:\n"
"log2p0 r3,r0\n"
"bswp8 r0,r0\n"
);
