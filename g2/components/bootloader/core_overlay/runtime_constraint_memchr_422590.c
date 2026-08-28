/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader constraint and memchr leaves. */

typedef __UINT8_TYPE__ open_cfw_constraint_u8;
typedef __UINT32_TYPE__ open_cfw_constraint_u32;
typedef void (*open_cfw_constraint_handler)(const char *, void *, open_cfw_constraint_u32);

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_constraint_default_417c28(const char *);
#define OPEN_CFW_CONSTRAINT_ATTR __attribute__((used, naked, noinline))
#else
extern open_cfw_constraint_handler open_cfw_constraint_host_handler;
void open_cfw_constraint_host_default(const char *);
#define OPEN_CFW_CONSTRAINT_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_CONSTRAINT_ATTR
open_cfw_constraint_u32 open_cfw_bootloader_constraint_dispatch_422590(const char *message)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r7, lr}\n"
        "cbnz r0, 1f\n"
        "adr r0, #24\n"
        "1:\n"
        "ldr r1, [pc, #0x14]\n"
        "ldr r3, [r1]\n"
        "cbz r3, 2f\n"
        "movs r2, #0x22\n"
        "movs r1, #0\n"
        "blx r3\n"
        "b 3f\n"
        "2:\n"
        "bl open_cfw_bootloader_constraint_default_417c28\n"
        "3:\n"
        "movs r0, #0x22\n"
        "pop {r1, pc}\n");
#else
    static const char bad_message[] = "constraint handler: bad message";
    if (message == (const char *)0) message = bad_message;
    if (open_cfw_constraint_host_handler != (open_cfw_constraint_handler)0)
        open_cfw_constraint_host_handler(message, (void *)0, 0x22U);
    else
        open_cfw_constraint_host_default(message);
    return 0x22U;
#endif
}

OPEN_CFW_CONSTRAINT_ATTR
void *open_cfw_bootloader_memchr_4225d0(const void *buffer, open_cfw_constraint_u32 value, open_cfw_constraint_u32 size)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "uxtb r1, r1\n"
        "1:\n"
        "lsls r3, r0, #30\n"
        "beq 3f\n"
        "subs r2, r2, #1\n"
        "blo 7f\n"
        "ldrb r3, [r0], #1\n"
        "cmp r1, r3\n"
        "bne 1b\n"
        "b 8f\n"
        "3:\n"
        "subs r2, #8\n"
        "blo 5f\n"
        "add.w r2, r2, #4\n"
        "orr.w r1, r1, r1, lsl #8\n"
        "orr.w r1, r1, r1, lsl #16\n"
        "4:\n"
        "ldr r3, [r0], #4\n"
        "subs r2, r2, #4\n"
        "itttt hs\n"
        "eorhs r3, r1\n"
        "subhs.w r12, r3, #0x01010101\n"
        "bichs.w r12, r12, r3\n"
        "tsths.w r12, #0x80808080\n"
        "beq 4b\n"
        "uxtb r1, r1\n"
        "subs r0, r0, #4\n"
        "5:\n"
        "adds r2, #8\n"
        "6:\n"
        "ldrb r3, [r0], #1\n"
        "subs r2, r2, #1\n"
        "it hs\n"
        "teqhs.w r1, r3\n"
        "bhi 6b\n"
        "7:\n"
        "it ne\n"
        "movne r0, #1\n"
        "8:\n"
        "subs r0, r0, #1\n"
        "bx lr\n");
#else
    const open_cfw_constraint_u8 *bytes = (const open_cfw_constraint_u8 *)buffer;
    open_cfw_constraint_u8 needle = (open_cfw_constraint_u8)value;
    while (size-- != 0U) {
        if (*bytes == needle) return (void *)bytes;
        ++bytes;
    }
    return (void *)0;
#endif
}
