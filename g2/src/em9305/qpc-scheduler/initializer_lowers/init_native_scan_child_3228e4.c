/* Native scan leaf; exact load and delayed-return contract. */
__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_scan_callback_3228e4\n"
".type opencfw_em9305_scan_callback_3228e4,@function\n"
"opencfw_em9305_scan_callback_3228e4:\n"
"L3228e4:\n"
"ld_s r0,[r0,0x2c]\n"
"L3228e6:\n"
"ld_s r0,[r0,0x6c]\n"
"L3228e8:\n"
"j_s.d [blink]\n"
"L3228ea:\n"
"setne r0,r0,0\n"
".size opencfw_em9305_scan_callback_3228e4,.-opencfw_em9305_scan_callback_3228e4\n"
);
