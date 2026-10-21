/* Native scan status action; tail-call with native delay-slot status. */
__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_scan_action_3255c0\n"
".type opencfw_em9305_scan_action_3255c0,@function\n"
"opencfw_em9305_scan_action_3255c0:\n"
"L3255c0:\n"
"b.d opencfw_em9305_command_status_30e8c0\n"
"L3255c4:\n"
"mov_s r0,0\n"
".size opencfw_em9305_scan_action_3255c0,.-opencfw_em9305_scan_action_3255c0\n"
);
