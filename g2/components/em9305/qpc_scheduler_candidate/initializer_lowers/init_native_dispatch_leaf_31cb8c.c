/* Native31cb8c..31cb9b full body and genuine selected children. */
__asm__(
    ".text\n"
    ".balign 4\n"
    ".global opencfw_em9305_dispatch_leaf_31cb8c\n"
    ".type opencfw_em9305_dispatch_leaf_31cb8c,@function\n"
    "opencfw_em9305_dispatch_leaf_31cb8c:\n"
    "push_s blink\n"
    "bl.d opencfw_em9305_common_request_30455c\n"
    "mov_s r0,1\n"
    "bl opencfw_em9305_command_count_30e4bc\n"
    "pop_s blink\n"
    "j_s [blink]\n"
    ".size opencfw_em9305_dispatch_leaf_31cb8c,.-opencfw_em9305_dispatch_leaf_31cb8c\n"
);
