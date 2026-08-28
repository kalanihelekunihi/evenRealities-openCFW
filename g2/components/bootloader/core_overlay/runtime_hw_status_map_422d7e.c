/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 per-instance status mapper. */

typedef __UINT32_TYPE__ open_cfw_hwsm_u32;

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_status_map_422d7e(void)
{
    __asm__ volatile(
        "ldr.w r3, [pc, #0x6c0]\n"
        "adds.w r3, r3, r2, lsl #12\n"
        "ldr r2, [r3, #0x3c]\n"
        "orrs r1, r2\n"
        "lsls r2, r1, #25\n"
        "bpl 1f\n"
        "ldr.w r0, [pc, #0x9d8]\n"
        "b 7f\n"
        "1:\n"
        "lsls r2, r1, #24\n"
        "bpl 2f\n"
        "ldr.w r0, [pc, #0x9d0]\n"
        "b 7f\n"
        "2:\n"
        "lsls r2, r1, #23\n"
        "bpl 3f\n"
        "ldr.w r0, [pc, #0x9cc]\n"
        "b 7f\n"
        "3:\n"
        "lsls r2, r1, #22\n"
        "bpl 4f\n"
        "ldr.w r0, [pc, #0x9c4]\n"
        "b 7f\n"
        "4:\n"
        "lsls r2, r1, #21\n"
        "bpl 5f\n"
        "ldr.w r0, [pc, #0x9c0]\n"
        "b 7f\n"
        "5:\n"
        "lsls r1, r1, #19\n"
        "bpl 7f\n"
        "ldr.w r0, [pc, #0xa68]\n"
        "7:\n"
        "bx lr\n");
}
#else
extern open_cfw_hwsm_u32 open_cfw_hwsm_host_registers[4][32];
open_cfw_hwsm_u32 open_cfw_bootloader_hw_status_map_422d7e(open_cfw_hwsm_u32 fallback,open_cfw_hwsm_u32 mask,open_cfw_hwsm_u32 index)
{
    open_cfw_hwsm_u32 value=mask|open_cfw_hwsm_host_registers[index][15];
    if(value&(1U<<6))return 0x08000006U;
    if(value&(1U<<7))return 0x08000007U;
    if(value&(1U<<8))return 0x08000008U;
    if(value&(1U<<9))return 0x08000009U;
    if(value&(1U<<10))return 0x0800000aU;
    if(value&(1U<<12))return 0x0800000bU;
    return fallback;
}
#endif
