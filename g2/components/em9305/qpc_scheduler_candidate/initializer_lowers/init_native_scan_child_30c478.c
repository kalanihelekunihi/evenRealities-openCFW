/* Authenticated four-byte native tail thunk to selected PRNG provider. */
__asm__(
".text\n"
".balign 4\n"
".global opencfw_em9305_scan_random_30c478\n"
".type opencfw_em9305_scan_random_30c478,@function\n"
"opencfw_em9305_scan_random_30c478:\n"
"L30c478:\n"
"b opencfw_em9305_pal_random_step\n"
".size opencfw_em9305_scan_random_30c478,.-opencfw_em9305_scan_random_30c478\n"
);
