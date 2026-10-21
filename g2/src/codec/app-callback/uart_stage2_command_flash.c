/* SPDX-License-Identifier: MIT
 * Flash command callback at stock 0x1000552c. Native supports the
 * `eraseall` and `erase` forms and rejects empty or trailing numeric text.
 */
#include <stdint.h>
#include "uart_stage2_command.h"

extern int32_t gx8002_uart_stage2_clock_rate_4b50(uint32_t selector);
extern uint32_t gx8002_uart_stage2_parse_unsigned_654c(
    const char *, char **, uint32_t);
extern void *gx8002_uart_stage2_flash_descriptor_33ac(
    uint32_t device, uint32_t mode, uint32_t clock, uint32_t block_size);
extern uint32_t gx8002_uart_stage2_callback_3418(const void *);
extern uint32_t gx8002_uart_stage2_callback_342c(
    const void *, uint32_t, uint32_t);

int32_t gx8002_uart_stage2_flash_552c(
    const struct gx8002_stage2_command *entry, uint32_t mode,
    uint32_t argc, char **argv)
{
    (void)entry;
    (void)mode;
    if (argc < 2u) return -1;
    uint32_t clock = (uint32_t)gx8002_uart_stage2_clock_rate_4b50(13u) >> 1;
    if (gx8002_uart_stage2_strcmp_6270(argv[1], "eraseall") == 0) {
        void *descriptor = gx8002_uart_stage2_flash_descriptor_33ac(
            0u, 0u, clock, 2048u);
        (void)gx8002_uart_stage2_callback_3418(descriptor);
        return 0;
    }
    if (gx8002_uart_stage2_strcmp_6270(argv[1], "erase") != 0 || argc < 4u)
        return -1;
    char *end;
    uint32_t offset = gx8002_uart_stage2_parse_unsigned_654c(
        argv[2], &end, 10u);
    if (argv[2][0] == '\0' || *end != '\0') return -1;
    uint32_t bytes = gx8002_uart_stage2_parse_unsigned_654c(
        argv[3], &end, 10u);
    if (argv[3][0] == '\0' || *end != '\0') return -1;
    void *descriptor = gx8002_uart_stage2_flash_descriptor_33ac(
        0u, 0u, clock, 2048u);
    (void)gx8002_uart_stage2_callback_342c(descriptor, offset, bytes);
    return 0;
}
