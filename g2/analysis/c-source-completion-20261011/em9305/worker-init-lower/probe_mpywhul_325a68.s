    .text
    .global opencfw_em9305_probe_mpywhul_325a68
opencfw_em9305_probe_mpywhul_325a68:
    mpywhul r18,r0,r1
    mpywhul r15,r0,r1
    mpyw_s r0,r0,r2
    j [blink]
