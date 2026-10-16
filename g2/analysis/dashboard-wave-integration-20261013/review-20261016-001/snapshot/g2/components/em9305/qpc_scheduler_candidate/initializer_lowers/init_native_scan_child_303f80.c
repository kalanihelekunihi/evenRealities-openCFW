/* Native scan leaf; exact load and delayed-return contract. */
__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_scan_current_303f80\n"
".type opencfw_em9305_scan_current_303f80,@function\n"
"opencfw_em9305_scan_current_303f80:\n"
"L303f80:\n"
"mov_s r0,0x805c18\n"
"L303f86:\n"
"ld r0,[r0,0]\n"
"L303f88:\n"
"j_s.d [blink]\n"
"L303f8a:\n"
"ldh_s r0,[r0,0x6]\n"
".size opencfw_em9305_scan_current_303f80,.-opencfw_em9305_scan_current_303f80\n"
);
