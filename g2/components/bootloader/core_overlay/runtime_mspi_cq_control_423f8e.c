/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of G2 MSPI command-queue enable/disable. */

typedef __UINT8_TYPE__ open_cfw_mcqc_u8;
typedef __UINT32_TYPE__ open_cfw_mcqc_u32;
typedef __UINTPTR_TYPE__ open_cfw_mcqc_uptr;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_mode_enable_route_4222f0(void);
extern void open_cfw_bootloader_retained_cmdq_enable_427878(void);
extern void open_cfw_bootloader_retained_cmdq_disable_4278c8(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_cq_enable_423f8e(void)
{
    __asm__ volatile(
        "push {r4, lr}\n"
        "movs r4, r0\n"
        "ldr r1, [r4, #4]\n"
        "adds r1, #0x10\n"
        "uxtb r1, r1\n"
        "movs r0, #4\n"
        "bl open_cfw_bootloader_mode_enable_route_4222f0\n"
        "cmp r0, #0\n"
        "bne 1f\n"
        "ldr.w r0, [r4, #0x828]\n"
        "bl open_cfw_bootloader_retained_cmdq_enable_427878\n"
        "1:\n"
        "pop {r4, pc}\n");
}

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_cq_disable_423fac(void)
{
    __asm__ volatile(
        "push {r7, lr}\n"
        "ldr.w r0, [r0, #0x828]\n"
        "bl open_cfw_bootloader_retained_cmdq_disable_4278c8\n"
        "pop {r1, pc}\n");
}
#else
typedef struct open_cfw_mcqc_context {
    open_cfw_mcqc_u32 reserved;
    open_cfw_mcqc_u32 module;
    open_cfw_mcqc_u8 gap[0x820];
    open_cfw_mcqc_uptr handle;
} open_cfw_mcqc_context;

typedef struct open_cfw_mcqc_ports {
    void *context;
    open_cfw_mcqc_u32 (*clock_request)(
        void *context, open_cfw_mcqc_u32 clock, open_cfw_mcqc_u8 user);
    open_cfw_mcqc_u32 (*cmdq_enable)(void *context, open_cfw_mcqc_uptr handle);
    open_cfw_mcqc_u32 (*cmdq_disable)(void *context, open_cfw_mcqc_uptr handle);
} open_cfw_mcqc_ports;

open_cfw_mcqc_u32 open_cfw_bootloader_mspi_cq_enable_423f8e(
    const open_cfw_mcqc_context *instance, const open_cfw_mcqc_ports *ports)
{
    open_cfw_mcqc_u32 status = ports->clock_request(
        ports->context, 4U, (open_cfw_mcqc_u8)(instance->module + 0x10U));
    if (status != 0U) return status;
    return ports->cmdq_enable(ports->context, instance->handle);
}

open_cfw_mcqc_u32 open_cfw_bootloader_mspi_cq_disable_423fac(
    const open_cfw_mcqc_context *instance, const open_cfw_mcqc_ports *ports)
{
    return ports->cmdq_disable(ports->context, instance->handle);
}
#endif
