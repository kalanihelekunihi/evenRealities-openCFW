/* Full native child; canonical existing children and explicit native no-op. */
__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_dispatch_noop_30fd30\n"
".type opencfw_em9305_dispatch_noop_30fd30,@function\n"
"opencfw_em9305_dispatch_noop_30fd30:\n"
"L30fd30:\n"
"j_s [blink]\n"
"L30fd32:\n"
"nop_s \n"
".size opencfw_em9305_dispatch_noop_30fd30,.-opencfw_em9305_dispatch_noop_30fd30\n"
);
