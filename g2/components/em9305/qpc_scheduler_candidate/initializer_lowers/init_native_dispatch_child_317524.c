/* Complete native helper; DSP accumulator and delay slot effects preserved. */
__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_dispatch_child_317524\n"
".type opencfw_em9305_dispatch_child_317524,@function\n"
"opencfw_em9305_dispatch_child_317524:\n"
"L317524:\n"
"mov_s r3,r2\n"
"L317526:\n"
"add r0,r0,0x8\n"
"L317528:\n"
"sub r2,r1,0xa\n"
"L31752c:\n"
"b.d opencfw_em9305_ll_event_enqueue\n"
"L317530:\n"
"mov_s r1,r3\n"
".size opencfw_em9305_dispatch_child_317524,.-opencfw_em9305_dispatch_child_317524\n"
);
