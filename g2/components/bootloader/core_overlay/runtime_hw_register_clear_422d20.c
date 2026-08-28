/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of two G2 per-instance register-clear leaves. */

typedef __UINT8_TYPE__ open_cfw_hwrc_u8;
typedef __UINT32_TYPE__ open_cfw_hwrc_u32;

#if defined(__arm__) || defined(__thumb__)
__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_register_clear_422d20(void)
{
    __asm__ volatile(
        "ldr r0, [r0, #0x28]\n"
        "ldr.w r1, [pc, #0x71c]\n"
        "movs r2, #0\n"
        "adds.w r3, r1, r0, lsl #12\n"
        "str r2, [r3, #0x48]\n"
        "adds.w r2, r1, r0, lsl #12\n"
        "adds r2, r2, #4\n"
        "ldr r3, [r2]\n"
        "bics r3, r3, #0x10\n"
        "str r3, [r2]\n"
        "adds.w r1, r1, r0, lsl #12\n"
        "adds r0, r1, #4\n"
        "ldr r1, [r0]\n"
        "bics r1, r1, #0x20\n"
        "str r1, [r0]\n"
        "bx lr\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_hw_register_clear_422d4c(void)
{
    __asm__ volatile(
        "ldr r0, [r0, #0x28]\n"
        "ldr.w r1, [pc, #0xa14]\n"
        "movs r2, #0\n"
        "adds.w r3, r1, r0, lsl #12\n"
        "str r2, [r3, #0x48]\n"
        "adds.w r2, r1, r0, lsl #12\n"
        "adds r2, r2, #4\n"
        "ldr r3, [r2]\n"
        "bics r3, r3, #0x20\n"
        "str r3, [r2]\n"
        "adds.w r1, r1, r0, lsl #12\n"
        "adds.w r0, r1, #0x50\n"
        "ldr r1, [r0]\n"
        "lsrs r1, r1, #12\n"
        "lsls r1, r1, #12\n"
        "str r1, [r0]\n"
        "bx lr\n");
}
#else
typedef struct { open_cfw_hwrc_u8 bytes[0x11c]; } open_cfw_hwrc_instance;
extern open_cfw_hwrc_u32 open_cfw_hwrc_host_registers[4][32];
static open_cfw_hwrc_u32 open_cfw_hwrc_read32(const open_cfw_hwrc_u8 *p)
{ return (open_cfw_hwrc_u32)p[0]|((open_cfw_hwrc_u32)p[1]<<8)|((open_cfw_hwrc_u32)p[2]<<16)|((open_cfw_hwrc_u32)p[3]<<24); }
void open_cfw_bootloader_hw_register_clear_422d20(open_cfw_hwrc_instance *instance)
{
    open_cfw_hwrc_u32 index=open_cfw_hwrc_read32(instance->bytes+0x28);
    open_cfw_hwrc_host_registers[index][18]=0;
    open_cfw_hwrc_host_registers[index][1]&=~0x30U;
}
void open_cfw_bootloader_hw_register_clear_422d4c(open_cfw_hwrc_instance *instance)
{
    open_cfw_hwrc_u32 index=open_cfw_hwrc_read32(instance->bytes+0x28);
    open_cfw_hwrc_host_registers[index][18]=0;
    open_cfw_hwrc_host_registers[index][1]&=~0x20U;
    open_cfw_hwrc_host_registers[index][20]&=~0xfffU;
}
#endif
