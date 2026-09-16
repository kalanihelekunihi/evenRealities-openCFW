/* SPDX-License-Identifier: MIT */
/* Complete peripheral shutdown at package 0x39b88. Status reads are
 * observable even though their values are discarded. */
extern void open_cfw_gx8002_stage1_gate(unsigned int module, unsigned int enable);
void open_cfw_gx8002_stage1_39b88(void)
{
    (void)*(volatile unsigned int *)0xa0500040;
    *(volatile unsigned int *)0xa0500030 = 0;
    *(volatile unsigned int *)0xa050006c = 0;
    (void)*(volatile unsigned int *)0xa0600040;
    *(volatile unsigned int *)0xa0600030 = 0;
    *(volatile unsigned int *)0xa060006c = 0;
    open_cfw_gx8002_stage1_gate(20, 0);
    open_cfw_gx8002_stage1_gate(21, 0);
}
