/* SPDX-License-Identifier: MIT */
/* Complete conditional register setup at package 0x39c44. */
extern __attribute__((noinline)) int open_cfw_gx8002_stage1_39824(void);
void open_cfw_gx8002_stage1_39c44(void)
{
    if (open_cfw_gx8002_stage1_39824() == 0) {
        volatile unsigned int *reg = (volatile unsigned int *)0xa0010094;
        *reg = (*reg & ~15u) | 12u;
    }
}

/* Stage-one trim predicate: unlike the backup reader, no gate call. */
int open_cfw_gx8002_stage1_39824(void)
{
    return *(volatile unsigned int *)0xa0010030 & 1u;
}
