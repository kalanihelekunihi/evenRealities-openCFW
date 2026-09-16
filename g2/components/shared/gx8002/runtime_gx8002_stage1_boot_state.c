/* SPDX-License-Identifier: MIT */
/* Package 0x39678: select flash boot state from the hardware descriptor.
 * Keep the second hardware read after publishing mode 2; the descriptor
 * may change between reads. */
extern void open_cfw_gx8002_stage1_39b88(void);
void open_cfw_gx8002_stage1_39678(void)
{
    open_cfw_gx8002_stage1_39b88();
    volatile unsigned int *descriptor = (volatile unsigned int *)0xa0010068;
    if ((*descriptor & 15u) == 2) {
        *(volatile unsigned int *)0x20001720 = 2;
        *(volatile unsigned int *)0x20001724 = *descriptor & ~255u;
    }
}
