/* Full native child; canonical existing children and explicit native no-op. */
__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_dispatch_child_302f70\n"
".type opencfw_em9305_dispatch_child_302f70,@function\n"
"opencfw_em9305_dispatch_child_302f70:\n"
"L302f70:\n"
"mov_s r1,0x8015cc\n"
"L302f76:\n"
"st_s r0,[r1,0xc]\n"
"L302f78:\n"
"b.d opencfw_em9305_common_radio_bind_30fc10\n"
"L302f7c:\n"
"mov_s r0,r1\n"
".size opencfw_em9305_dispatch_child_302f70,.-opencfw_em9305_dispatch_child_302f70\n"
);
