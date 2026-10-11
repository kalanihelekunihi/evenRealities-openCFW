/* SPDX-License-Identifier: MIT
 * Stage-2 serial flash download command 0x10005628. Native control uses
 * alternating L/R UART receive buffers, a flash-program callback, and
 * the stock rolling checksum. Hardware timing is not yet qualified.
 */
#include <stdint.h>
#include "uart_stage2_command.h"

extern uint32_t gx8002_uart_stage2_parse_unsigned_654c(
    const char *, char **, uint32_t);
extern void *gx8002_uart_stage2_pool_malloc_6134(uint32_t);
extern void gx8002_uart_stage2_pool_free_wrapper_6168(void *);
extern int32_t gx8002_uart_stage2_clock_rate_4b50(uint32_t);
extern void *gx8002_uart_stage2_flash_descriptor_33ac(
    uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_uart_stage2_callback_3444(const void *);
extern uint32_t gx8002_uart_stage2_callback_342c(
    const void *, uint32_t, uint32_t);
extern int32_t gx8002_uart_stage2_callback_write_3458(
    const void *, uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_uart_stage2_console_getc_2a74(void);
extern uint32_t gx8002_uart_stage2_uart_start_2f34(
    uint32_t, uint32_t, uint32_t, uint32_t, uint32_t);
extern uint32_t gx8002_uart_stage2_serialdown_done_55e0(
    uint32_t, const char *);
extern void gx8002_uart_stage2_serialdown_finish_token_5604(void);
extern void gx8002_uart_stage2_console_putc_2a60(uint32_t);
extern uint32_t gx8002_uart_stage2_checksum_66b8(
    uint32_t, const void *, uint32_t);

static void send_start_token(void)
{
    static const char token[] = "~sta~";
    for (uint32_t i = 0; i < sizeof(token) - 1u; ++i)
        gx8002_uart_stage2_console_putc_2a60((uint8_t)token[i]);
}

static int parse_argument(const char *text, uint32_t *value)
{
    char *end;
    *value = gx8002_uart_stage2_parse_unsigned_654c(text, &end, 10u);
    return *text != '\0' && *end == '\0';
}

int32_t gx8002_uart_stage2_serialdown_5628(
    const struct gx8002_stage2_command *entry, uint32_t mode,
    uint32_t argc, char **argv)
{
    (void)entry;
    (void)mode;
    volatile const uint32_t *uart_mode =
        (volatile const uint32_t *)(uintptr_t)UINT32_C(0x20009084);
    uint32_t port = uart_mode[0] != 0u ? 0u : (uart_mode[1] == 1u);
    if (argc < 4u) return -1;
    uint32_t base, total, maximum;
    if (!parse_argument(argv[1], &base) ||
        !parse_argument(argv[2], &total) ||
        !parse_argument(argv[3], &maximum)) return -1;

    uint32_t capacity = total < maximum ? total : maximum;
    void *left = gx8002_uart_stage2_pool_malloc_6134(capacity);
    if (left == 0) {
        gx8002_uart_stage2_launch_61a4(
            "%s memalloc failed, %d\n", "do_serialdown", maximum);
        return -1;
    }
    void *right = total < maximum ? left :
        gx8002_uart_stage2_pool_malloc_6134(maximum);
    if (right == 0) {
        gx8002_uart_stage2_pool_free_wrapper_6168(left);
        gx8002_uart_stage2_launch_61a4(
            "%s memalloc failed, %d\n", "do_serialdown", maximum);
        return -1;
    }
    uint32_t clock = (uint32_t)gx8002_uart_stage2_clock_rate_4b50(13u) >> 1;
    void *descriptor = gx8002_uart_stage2_flash_descriptor_33ac(
        0u, 0u, clock, 2048u);
    *(volatile uint32_t *)(uintptr_t)UINT32_C(0x20009970) =
        (uint32_t)(uintptr_t)descriptor;
    int32_t result = 0;
    if (descriptor == 0) {
        gx8002_uart_stage2_launch_61a4("spi flash probe error!\n");
        result = -1;
        goto cleanup;
    }
    if ((int32_t)gx8002_uart_stage2_callback_3444(descriptor) < 0) {
        gx8002_uart_stage2_launch_61a4(
            "spi flash write protect unlock error!\n");
        result = -1;
        goto cleanup;
    }
    uint32_t received_checksum = 0;
    for (uint32_t i = 0; i < 4u; ++i)
        received_checksum |= (gx8002_uart_stage2_console_getc_2a74() & 0xffu)
                             << (i * 8u);
    uint32_t calculated = 0;
    uint32_t offset = 0;
    uint32_t remaining = total;
    uint32_t previous_size = 0;
    uint8_t *previous_buffer = 0;
    char phase = 'L';
    for (;;) {
        uint32_t current_size = remaining < maximum ? remaining : maximum;
        uint8_t *current_buffer = (uint8_t *)(phase == 'L' ? left : right);
        volatile uint32_t *done = (volatile uint32_t *)(uintptr_t)
            (phase == 'L' ? UINT32_C(0x2000a154) : UINT32_C(0x2000a150));
        *done = 0u;
        (void)gx8002_uart_stage2_uart_start_2f34(
            port, (uint32_t)(uintptr_t)current_buffer, current_size,
            (uint32_t)(uintptr_t)&gx8002_uart_stage2_serialdown_done_55e0,
            (uint32_t)(uintptr_t)&phase);
        if (previous_buffer != 0)
            gx8002_uart_stage2_serialdown_finish_token_5604();
        send_start_token();
        if (previous_buffer == 0) {
            (void)gx8002_uart_stage2_callback_342c(descriptor, base, total);
        } else {
            int32_t write = gx8002_uart_stage2_callback_write_3458(
                descriptor, base, offset,
                (uint32_t)(uintptr_t)previous_buffer, previous_size);
            if (write != 0) {
                gx8002_uart_stage2_launch_61a4(
                    "flash program failed, offset : 0x%x, pos : 0x%x len : %d, ret :%d\n",
                    base, offset, previous_size, write);
                result = 1; /* Native stores subsequent-pass r9 here. */
            }
            calculated = gx8002_uart_stage2_checksum_66b8(
                calculated, previous_buffer, previous_size);
            offset += previous_size;
        }
        while (*done == 0u) { }
        remaining -= current_size;
        previous_buffer = current_buffer;
        previous_size = current_size;
        if (remaining == 0u) break;
        phase = phase == 'L' ? 'R' : 'L';
    }
    {
        int32_t write = gx8002_uart_stage2_callback_write_3458(
            descriptor, base, offset,
            (uint32_t)(uintptr_t)previous_buffer, previous_size);
        if (write != 0) {
            gx8002_uart_stage2_launch_61a4(
                "flash program failed, offset : 0x%x, pos : 0x%x len : %d, ret :%d\n",
                base, offset, previous_size, write);
            result = -1;
        }
        calculated = gx8002_uart_stage2_checksum_66b8(
            calculated, previous_buffer, previous_size);
    }
    gx8002_uart_stage2_serialdown_finish_token_5604();
    if (result == 0 && calculated != received_checksum) {
        gx8002_uart_stage2_launch_61a4(
            "crc failed, recv : %x, cal : %x\n",
            received_checksum, calculated);
        result = -1;
    }
cleanup:
    if (right != left) gx8002_uart_stage2_pool_free_wrapper_6168(right);
    gx8002_uart_stage2_pool_free_wrapper_6168(left);
    return result;
}
