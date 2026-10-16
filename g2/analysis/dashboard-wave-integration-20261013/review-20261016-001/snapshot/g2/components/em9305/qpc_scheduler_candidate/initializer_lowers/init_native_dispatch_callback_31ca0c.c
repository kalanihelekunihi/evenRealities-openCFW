/* Complete native 31ca0c callback that allocates and submits a command. */
__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_dispatch_callback_31ca0c\n"
".type opencfw_em9305_dispatch_callback_31ca0c,@function\n"
"opencfw_em9305_dispatch_callback_31ca0c:\n"
"enter_s [r13,blink]\n"
"mov_s r13,r0\n"
"mov_s r0,0x8029ac\n"
"mov_s r1,0\n"
"bl.d opencfw_em9305_memset\n"
"mov_s r2,0x88\n"
"bl.d opencfw_em9305_dispatch_callback_31ceb4\n"
"mov_s r0,r13\n"
"leave_s [r13,blink,pcl]\n"
".size opencfw_em9305_dispatch_callback_31ca0c,.-opencfw_em9305_dispatch_callback_31ca0c\n"
);
