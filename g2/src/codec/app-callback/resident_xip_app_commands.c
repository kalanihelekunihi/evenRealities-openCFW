/* SPDX-License-Identifier: MIT
 * Native image-A XIP 0x10209258..0x102093a6. Eleven 28-byte stack
 * registrations, their exact IDs/name strings, two payload descriptors,
 * and original registration call order are taken from direct C-SKY code.
 */
#include <stdint.h>

extern int32_t gx8002_xip_uart_async_register_102082ac(const uint8_t *);
extern void gx8002_xip_memset_102099cc(void *, uint32_t, uint32_t);
extern uint32_t gx8002_xip_app_command_callback_persistent_10209430(
    const uint8_t *);

struct gx8002_command_registration {
    uint32_t type;
    uint32_t identity;
    uint32_t payload_address;
    uint32_t payload_bytes;
    uint32_t context;
    uint32_t callback;
    const char *name;
};
_Static_assert(sizeof(struct gx8002_command_registration) == 28u,
               "native application registration stride");

int32_t gx8002_xip_app_commands_10209258(void)
{
    static const uint16_t identity[11] = {
        368u, 369u, 258u, 263u, 265u, 266u,
        267u, 268u, 269u, 270u, 271u
    };
    static const char *const name[11] = {
        "mic status", "gsensor status", "version", "switch bf cmd",
        "open vad reporting", "close vad reporting", "set pga gain",
        "start Dmic cmd", "close Dmic cmd", "pdm ch delay",
        "i2s set state"
    };
    struct gx8002_command_registration registration[11];
    for (uint32_t index = 0u; index < 11u; ++index) {
        gx8002_xip_memset_102099cc(&registration[index], 0u, 28u);
        registration[index].identity = identity[index];
        registration[index].callback =
            (uint32_t)(uintptr_t)
                &gx8002_xip_app_command_callback_persistent_10209430;
        registration[index].name = name[index];
    }
    for (uint32_t index = 6u; index <= 10u; index += 4u) {
        registration[index].payload_address = UINT32_C(0x2002e8f0);
        registration[index].payload_bytes = 32u;
    }
    int32_t result = 0;
    for (uint32_t index = 0u; index < 11u; ++index)
        result = gx8002_xip_uart_async_register_102082ac(
            (const uint8_t *)&registration[index]);
    return result;
}
