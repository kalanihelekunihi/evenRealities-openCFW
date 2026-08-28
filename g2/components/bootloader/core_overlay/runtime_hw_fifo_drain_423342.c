/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 per-instance FIFO drain wrapper. */

typedef __UINT8_TYPE__ open_cfw_hwfifod_u8;
typedef __UINT32_TYPE__ open_cfw_hwfifod_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_hw_fifo_read_4232c8(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_fifo_drain_423342(void)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "movs r3, #0\n"
        "movs r2, #0x20\n"
        "movs r1, #0\n"
        "bl open_cfw_bootloader_hw_fifo_read_4232c8\n"
        "pop {r1, pc}\n");
}
#else
typedef struct open_cfw_hwfifod_instance { open_cfw_hwfifod_u8 bytes[0x11c]; } open_cfw_hwfifod_instance;
extern open_cfw_hwfifod_u32 open_cfw_hwfifod_host_read(open_cfw_hwfifod_instance *instance, open_cfw_hwfifod_u8 *output, open_cfw_hwfifod_u32 capacity, open_cfw_hwfifod_u32 *count);

open_cfw_hwfifod_u32 open_cfw_bootloader_hw_fifo_drain_423342(open_cfw_hwfifod_instance *instance)
{
    return open_cfw_hwfifod_host_read(instance, (open_cfw_hwfifod_u8 *)0, 32U, (open_cfw_hwfifod_u32 *)0);
}
#endif
