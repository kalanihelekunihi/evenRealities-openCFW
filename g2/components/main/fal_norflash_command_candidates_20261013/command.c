/* SPDX-License-Identifier: MIT
 * Main 0x470168: MX25U read command request construction and dispatch.
 * The MSPI transfer at 0x4c2098 and live controller handle are lowers.
 */
#include <stdint.h>
#include <stddef.h>

extern volatile uint32_t g2_norflash_controller_handle_20074544;
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x48949c */
extern uint32_t g2_norflash_transfer_4c2098(uint32_t controller,
                                              const void *request,
                                              uint32_t timeout);
extern void g2_norflash_diagnostic_4733ee(const char *, ...);

struct nor_read_request {
    uint32_t count;
    uint8_t reserved4;
    uint8_t reserved5;
    uint8_t reserved6;
    uint8_t has_address;
    uint32_t address;
    uint16_t transfer_count;
    uint16_t command;
    uint8_t enabled;
    uint8_t reserved17;
    uint8_t reserved18;
    uint8_t reserved19;
    uint32_t response_pointer;
};
_Static_assert(sizeof(struct nor_read_request) == 24u, "native MSPI request size");
_Static_assert(offsetof(struct nor_read_request, response_pointer) == 20u,
               "native response pointer offset");

static const char transfer_failed[] =
    "MSPI read xfer failed: instr=0x%02X, addr=0x%08X, len=%u, hal_st=%d\n";

uint32_t g2_norflash_command_470168(uint32_t command, uint32_t address,
                                      uint32_t mode, uint8_t *response,
                                      uint32_t count)
{
    struct nor_read_request request;
    audio_uart_buffer_zero(&request, 24u, 0u);
    uint32_t controller = g2_norflash_controller_handle_20074544;
    if (controller == 0u) return 2u;
    if (response == NULL || count == 0u) return 6u;
    if (address >= 0x02000000u) return 5u;

    request.reserved6 = 0u;
    request.has_address = (uint8_t)mode != 0u;
    request.address = request.has_address ? address : 0u;
    request.transfer_count = 1u;
    request.command = (uint16_t)command;
    request.enabled = 1u;
    request.count = count;
    request.response_pointer = (uint32_t)(uintptr_t)response;
    request.reserved5 = 0u;
    request.reserved17 = 0u;

    uint32_t result = g2_norflash_transfer_4c2098(controller, &request,
                                                    1000000u);
    if (result != 0u)
        g2_norflash_diagnostic_4733ee(transfer_failed, (uint16_t)command,
                                      address, count, result);
    return result;
}
