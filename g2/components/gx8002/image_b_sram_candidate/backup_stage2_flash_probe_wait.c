/* Native image-B 0x10007fac..0x10007ffc. Poll the product's typed flash
 * probe callback until it returns a device or the 5,000,000-tick window
 * expires. The initialized callback word and probe state remain genuine
 * data/BSS placement contracts; no flash device is synthesized.
 */
#include <stdint.h>

extern uint64_t gx8002_image_b_time_10005070(void);
extern uintptr_t gx8002_image_b_flash_probe_callback_20016d80[31];
extern volatile uint8_t gx8002_image_b_flash_probe_state_2001765c;

uint32_t gx8002_image_b_flash_probe_10007fac(uint32_t bus,
                                               uint32_t chip_select,
                                               uint32_t speed,
                                               uint32_t mode)
{
    uint64_t start = gx8002_image_b_time_10005070();
    for (;;) {
        if (gx8002_image_b_flash_probe_state_2001765c < 2u) {
            uint32_t callback =
                (uint32_t)gx8002_image_b_flash_probe_callback_20016d80[0];
            uint32_t device = ((uint32_t (*)(uint32_t, uint32_t,
                                uint32_t, uint32_t))(uintptr_t)callback)(
                                    bus, chip_select, speed, mode);
            if (device != 0u) {
                gx8002_image_b_flash_probe_state_2001765c = 1u;
                return device;
            }
        }
        if (gx8002_image_b_time_10005070() - start >
            UINT64_C(0x004c4b3f))
            return 0u;
    }
}
