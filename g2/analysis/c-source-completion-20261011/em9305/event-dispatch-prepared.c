/* Native306c7c..306c8a dynamic tail preserves all inherited registers; R0 is the loaded callback address. */
__asm__(
".text\n.balign 4\n.global opencfw_em9305_init_event_dispatch_306c7c\n.type opencfw_em9305_init_event_dispatch_306c7c,@function\nopencfw_em9305_init_event_dispatch_306c7c:\nld.as r0,[0x802878,r0]\ncmp_s r0,0\njeq_s [blink]\nj_s [r0]\nnop_s\n.size opencfw_em9305_init_event_dispatch_306c7c,.-opencfw_em9305_init_event_dispatch_306c7c\n"
);
