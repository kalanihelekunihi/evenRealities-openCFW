/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 MSPI command-queue terminator. */

typedef __UINT8_TYPE__ open_cfw_mcqt_u8;
typedef __UINT32_TYPE__ open_cfw_mcqt_u32;
typedef __UINTPTR_TYPE__ open_cfw_mcqt_uptr;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_retained_cmdq_term_427ad6(void);

__attribute__((used, naked, noinline))
void open_cfw_bootloader_mspi_cq_term_423f54(void)
{
    __asm__ volatile(
        "push {r4, r5, r6, lr}\n"
        "ldr r4, [r0, #4]\n"
        "mov.w r5, #0x8d0\n"
        /* Fixed literal load from 0x00423F5C to 0x00424AEC. */
        "ldr.w r6, [pc, #0xb8c]\n"
        "mul r0, r5, r4\n"
        "add r0, r6\n"
        "ldr.w r0, [r0, #0x828]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "movs r1, #1\n"
        "mul r0, r5, r4\n"
        "add r0, r6\n"
        "ldr.w r0, [r0, #0x828]\n"
        "bl open_cfw_bootloader_retained_cmdq_term_427ad6\n"
        "movs r0, #0\n"
        "muls r4, r5, r4\n"
        "add.w r1, r6, r4\n"
        "str.w r0, [r1, #0x828]\n"
        "1:\n"
        "movs r0, #0\n"
        "pop {r4, r5, r6, pc}\n");
}
#else
typedef struct open_cfw_mcqt_context {
    open_cfw_mcqt_u32 reserved;
    open_cfw_mcqt_u32 module;
} open_cfw_mcqt_context;

typedef struct open_cfw_mcqt_ports {
    void *context;
    void (*cmdq_term)(void *context, open_cfw_mcqt_uptr handle,
                      open_cfw_mcqt_u32 force);
} open_cfw_mcqt_ports;

open_cfw_mcqt_u32 open_cfw_bootloader_mspi_cq_term_423f54(
    const open_cfw_mcqt_context *instance, open_cfw_mcqt_uptr *handles,
    const open_cfw_mcqt_ports *ports)
{
    open_cfw_mcqt_u32 module = instance->module;
    open_cfw_mcqt_uptr handle = handles[module];

    if (handle != (open_cfw_mcqt_uptr)0) {
        ports->cmdq_term(ports->context, handle, 1U);
        handles[module] = (open_cfw_mcqt_uptr)0;
    }
    return 0U;
}
#endif
