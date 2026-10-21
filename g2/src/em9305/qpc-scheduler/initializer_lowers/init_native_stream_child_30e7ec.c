/* Native stream event tail thunk; event word stored in branch delay slot. */
__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_stream_stop_30e7ec\n"
".type opencfw_em9305_stream_stop_30e7ec,@function\n"
"opencfw_em9305_stream_stop_30e7ec:\n"
"L30e7ec:\n"
"mov_s r1,0x17\n"
"L30e7ee:\n"
"asl_s r1,r1,0x10\n"
"L30e7f0:\n"
"b.d opencfw_em9305_ll_event_callback_30e79c\n"
"L30e7f4:\n"
"st_s r1,[r0,0]\n"
".size opencfw_em9305_stream_stop_30e7ec,.-opencfw_em9305_stream_stop_30e7ec\n"
);
