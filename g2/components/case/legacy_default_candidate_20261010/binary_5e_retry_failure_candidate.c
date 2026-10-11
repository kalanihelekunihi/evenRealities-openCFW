/* SPDX-License-Identifier: MIT
 * Isolated stock 0x0800373c read-failure branch: all three flash reads fail.
 * Not a full case_binary_5e_apply provider.
 */
#include <stdint.h>

extern uint32_t case_binary_5e_flash_mode(void);
extern uint32_t case_binary_5e_flash_init(void);
extern uint32_t case_binary_5e_flash_read(void *configuration, uint32_t *error);
extern uint32_t case_binary_5e_wait(uint32_t ticks);
extern uint32_t case_binary_5e_flash_finish(void);
extern uint32_t case_binary_5e_failure_log(const char *format, ...);

uint32_t case_binary_5e_retry_failure_candidate(const uint8_t *sixteen)
{
    (void)sixteen;
    volatile uint32_t *config = (volatile uint32_t *)(uintptr_t)0x200001a4u;
    config[0] = 2u;
    uint32_t mode = case_binary_5e_flash_mode();
    config[1] = mode == 1u ? 4u : 0x8000u;
    config[2] = 0x7eu;
    config[3] = 1u;
    case_binary_5e_flash_init();
    uint32_t error = 0u;
    for (uint32_t retry = 0; retry < 3u; ++retry) {
        case_binary_5e_flash_read((void *)(uintptr_t)0x200001a4u, &error);
        case_binary_5e_wait(10u);
    }
    if (*(volatile uint8_t *)(uintptr_t)0x200000bfu == 0u) {
        case_binary_5e_failure_log("fail to erase. err:0x%x", error);
        case_binary_5e_failure_log("\r\n");
    }
    case_binary_5e_flash_finish();
    return 0u;
}
