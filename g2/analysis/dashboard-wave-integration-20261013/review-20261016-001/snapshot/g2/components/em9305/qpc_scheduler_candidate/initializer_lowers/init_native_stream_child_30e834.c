/* Native stream event tail thunk; event word stored in branch delay slot. */
__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_stream_release_30e834\n"
".type opencfw_em9305_stream_release_30e834,@function\n"
"opencfw_em9305_stream_release_30e834:\n"
"L30e834:\n"
"mov_s r1,0\n"
"L30e836:\n"
"bset_s r1,r1,0x15\n"
"L30e838:\n"
"b.d opencfw_em9305_ll_event_callback_30e79c\n"
"L30e83c:\n"
"st_s r1,[r0,0]\n"
".size opencfw_em9305_stream_release_30e834,.-opencfw_em9305_stream_release_30e834\n"
);
