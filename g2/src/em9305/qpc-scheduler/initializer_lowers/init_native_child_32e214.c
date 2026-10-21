__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_child_32e214\n"
".type opencfw_em9305_child_32e214,@function\n"
"opencfw_em9305_child_32e214:\n"
"L32e214:\n"
"add r0,r0,403\n"
"L32e218:\n"
"j_s.d [blink]\n"
"L32e21a:\n"
"stb 0,[r0]\n"
".size opencfw_em9305_child_32e214,.-opencfw_em9305_child_32e214\n"
);
