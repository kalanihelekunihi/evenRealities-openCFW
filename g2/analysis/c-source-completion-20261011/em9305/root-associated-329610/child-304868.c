/* Complete native304868..304880; caller-visible register effects retained. */
__asm__(
".text\n.balign 4\n.global opencfw_em9305_associated_child_304868\n"
".type opencfw_em9305_associated_child_304868,@function\n"
"opencfw_em9305_associated_child_304868:\n"
"mov_s r0,0x805f00\n"
"ldb_s r0,[r0,0]\n"
"breq_s r0,0,L30487c\n"
"mov_s r0,0x8012fc\n"
"j_s.d [blink]\n"
"ldb_s r0,[r0,0]\n"
"L30487c: j_s.d [blink]\n"
"mov_s r0,0xff\n"
".size opencfw_em9305_associated_child_304868,.-opencfw_em9305_associated_child_304868\n"
);
