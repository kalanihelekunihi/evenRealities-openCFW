/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MSPI command-queue initializer. */

typedef __UINT8_TYPE__ open_cfw_mcqi_u8;
typedef __UINT32_TYPE__ open_cfw_mcqi_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_cmdq_init_427794(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_cq_init_423f28(void)
{
    __asm__ volatile(
        "push {r5, r6, r7, lr}\n"
        "str r2, [sp, #4]\n"
        "lsrs r1, r1, #1\n"
        "str r1, [sp]\n"
        "movs r1, #1\n"
        "strb.w r1, [sp, #8]\n"
        /* Fixed literal load from 0x00423F36 to 0x00424AEC. */
        "ldr.w r1, [pc, #0xbb4]\n"
        "mov.w r2, #0x8d0\n"
        "mul r2, r2, r0\n"
        "add r1, r2\n"
        "addw r2, r1, #0x828\n"
        "mov r1, sp\n"
        "adds r0, #8\n"
        "uxtb r0, r0\n"
        "bl open_cfw_bootloader_retained_cmdq_init_427794\n"
        "pop {r1, r2, r3, pc}\n");
}
#else
typedef struct open_cfw_mcqi_config {
    open_cfw_mcqi_u32 size;
    const open_cfw_mcqi_u32 *buffer;
    open_cfw_mcqi_u8 priority;
} open_cfw_mcqi_config;

typedef struct open_cfw_mcqi_ports {
    void *context;
    open_cfw_mcqi_u32 (*cmdq_init)(
        void *context, open_cfw_mcqi_u8 interface,
        const open_cfw_mcqi_config *config,
        open_cfw_mcqi_u32 handle_slot_address);
} open_cfw_mcqi_ports;

open_cfw_mcqi_u32 open_cfw_bootloader_mspi_cq_init_423f28(
    open_cfw_mcqi_u32 module, open_cfw_mcqi_u32 length,
    const open_cfw_mcqi_u32 *buffer, const open_cfw_mcqi_ports *ports)
{
    open_cfw_mcqi_config config;
    open_cfw_mcqi_u32 slot;

    if (ports == (const open_cfw_mcqi_ports *)0 ||
        ports->cmdq_init == (void *)0)
        return 0xffffffffU;
    config.size = length >> 1;
    config.buffer = buffer;
    config.priority = 1U;
    slot = 0x2001caa0U + module * 0x8d0U + 0x828U;
    return ports->cmdq_init(
        ports->context, (open_cfw_mcqi_u8)(module + 8U), &config, slot);
}
#endif
