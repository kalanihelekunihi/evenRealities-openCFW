/* SPDX-License-Identifier: MIT
 * Main 0x47021c: MX25U write command request construction and dispatch.
 * The MSPI transfer at 0x4c2098 and live controller handle remain lowers.
 */
#include <stdint.h>
#include <stddef.h>

extern volatile uint32_t g2_norflash_controller_handle_20074544;
extern void audio_uart_buffer_zero(void *, uint32_t, uint32_t); /* 0x48949c */
extern uint32_t g2_norflash_transfer_4c2098(uint32_t controller,
                                              const void *request,
                                              uint32_t timeout);
extern void g2_norflash_diagnostic_4733ee(const char *, ...);

struct nor_write_request {
    uint32_t count;
    uint8_t reserved4;
    uint8_t reserved5;
    uint8_t has_data;
    uint8_t has_address;
    uint32_t address;
    uint16_t transfer_count;
    uint16_t command;
    uint8_t disabled;
    uint8_t reserved17;
    uint8_t reserved18;
    uint8_t reserved19;
    uint32_t data_pointer;
};
_Static_assert(sizeof(struct nor_write_request) == 24u, "native MSPI request size");
_Static_assert(offsetof(struct nor_write_request, data_pointer) == 20u,
               "native data pointer offset");

static const char transfer_failed[] =
    "MSPI write xfer failed: instr=0x%02X, addr=0x%08X, len=%u, hal_st=%d\n";

uint32_t g2_norflash_erase_command_47021c(uint32_t command,
                                             uint32_t address,
                                             uint32_t mode,
                                             uint32_t data_pointer,
                                             uint32_t count)
{
    if (g2_norflash_controller_handle_20074544 == 0u) return 2u;
    struct nor_write_request request;
    audio_uart_buffer_zero(&request, 24u, 0u);
    if (address >= 0x02000000u || count > 256u) return 5u;

    request.has_data = 1u;
    request.has_address = (uint8_t)mode != 0u;
    request.address = request.has_address ? address : 0u;
    request.transfer_count = 1u;
    request.command = (uint16_t)command;
    request.disabled = 0u;
    request.count = count;
    request.data_pointer = data_pointer;
    request.reserved5 = 0u;
    request.reserved17 = 0u;

    uint32_t controller = g2_norflash_controller_handle_20074544;
    uint32_t result = g2_norflash_transfer_4c2098(controller, &request,
                                                    1000000u);
    if (result != 0u)
        g2_norflash_diagnostic_4733ee(transfer_failed, (uint16_t)command,
                                      address, count, result);
    return result;
}
