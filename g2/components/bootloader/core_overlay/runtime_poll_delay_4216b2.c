/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of the G2 bootloader bounded poll-delay helper. */

typedef __UINT8_TYPE__ open_cfw_poll_u8;
typedef __UINT32_TYPE__ open_cfw_poll_u32;

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_delay_41d1c0(open_cfw_poll_u32 duration);
#define OPEN_CFW_POLL_ATTR __attribute__((used, naked, noinline))
#else
void open_cfw_poll_host_delay(open_cfw_poll_u32 duration);
#define OPEN_CFW_POLL_ATTR __attribute__((used, noinline))
#endif

OPEN_CFW_POLL_ATTR
void open_cfw_bootloader_poll_delay_4216b2(
    volatile open_cfw_poll_u8 *active,
    volatile open_cfw_poll_u32 *remaining)
{
#if defined(__arm__) || defined(__thumb__)
    __asm__ volatile(
        "push {r3, r4, r5, lr}\n"
        "movs r4, r0\n"
        "movs r5, r1\n"
        "b 2f\n"
        "1:\n"
        "movs r0, #10\n"
        "bl open_cfw_bootloader_delay_41d1c0\n"
        "ldr r0, [r5]\n"
        "subs r0, r0, #1\n"
        "str r0, [r5]\n"
        "2:\n"
        "ldr r0, [r5]\n"
        "cmp r0, #0\n"
        "beq 3f\n"
        "ldrb r0, [r4]\n"
        "cmp r0, #0\n"
        "bne 1b\n"
        "3:\n"
        "pop {r0, r4, r5, pc}\n");
#else
    while (*remaining != 0U && *active != 0U) {
        open_cfw_poll_host_delay(10U);
        *remaining -= 1U;
    }
#endif
}
