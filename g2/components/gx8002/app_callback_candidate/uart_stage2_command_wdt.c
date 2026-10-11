/* SPDX-License-Identifier: MIT
 * Native stage-2 `wdt` command callback at stock 0x10005978. Its four
 * subcommands, strings, and A001 watchdog register offsets are directly
 * attributable to the authenticated stage-2 image.
 */
#include <stdint.h>
#include "uart_stage2_command.h"

extern uint32_t gx8002_uart_stage2_parse_unsigned_654c(
    const char *text, char **end, uint32_t base);
extern void gx8002_uart_stage2_watchdog_configure_4478(
    uint32_t doubled, uint32_t value, uint32_t (*callback)(void));
extern uint32_t gx8002_uart_stage2_watchdog_callback_5958(void);
extern void gx8002_uart_stage2_watchdog_kick_44fc(void);

int32_t gx8002_uart_stage2_wdt_5978(
    const struct gx8002_stage2_command *entry, uint32_t mode,
    uint32_t argc, char **argv)
{
    (void)entry;
    (void)mode;
    if (argc < 2u) return -1;
    if (gx8002_uart_stage2_strcmp_6270("init", argv[1]) == 0) {
        char *end = 0;
        uint32_t value = gx8002_uart_stage2_parse_unsigned_654c(
            argv[2], &end, 10u) & UINT32_C(0xffff);
        gx8002_uart_stage2_watchdog_configure_4478(
            (value << 1) & UINT32_C(0xffff), value,
            gx8002_uart_stage2_watchdog_callback_5958);
        return 0;
    }
    if (gx8002_uart_stage2_strcmp_6270("ping", argv[1]) == 0) {
        gx8002_uart_stage2_watchdog_kick_44fc();
        return 0;
    }
    if (gx8002_uart_stage2_strcmp_6270("write", argv[1]) == 0) {
        char *end = 0;
        uint32_t value = gx8002_uart_stage2_parse_unsigned_654c(
            argv[2], &end, 10u);
        *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa001002c) = value;
        *(volatile uint32_t *)(uintptr_t)UINT32_C(0xa0010030) = value;
        return 0;
    }
    if (gx8002_uart_stage2_strcmp_6270("read", argv[1]) == 0) {
        uint32_t first = *(volatile const uint32_t *)(uintptr_t)
            UINT32_C(0xa001002c);
        uint32_t second = *(volatile const uint32_t *)(uintptr_t)
            UINT32_C(0xa0010030);
        gx8002_uart_stage2_launch_61a4("0x%x, 0x%x\n", first, second);
        return 0;
    }
    gx8002_uart_stage2_launch_61a4("Unsupport cmd\n");
    return 0;
}
