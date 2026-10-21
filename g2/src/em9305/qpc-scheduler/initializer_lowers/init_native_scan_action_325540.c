/* Native scan status action; tail-call with native delay-slot status. */
__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_scan_action_325540\n"
".type opencfw_em9305_scan_action_325540,@function\n"
"opencfw_em9305_scan_action_325540:\n"
"L325540:\n"
"b.d opencfw_em9305_command_status_30e8c0\n"
"L325544:\n"
"mov_s r0,0xc\n"
".size opencfw_em9305_scan_action_325540,.-opencfw_em9305_scan_action_325540\n"
);
