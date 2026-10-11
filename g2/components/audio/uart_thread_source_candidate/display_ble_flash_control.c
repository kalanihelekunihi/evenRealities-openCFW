/* Native registered HAL callback dispatch 0x480312. */
#include <stdint.h>
typedef uint32_t (*audio_ble_flash_control_fn)(uint8_t, uint8_t, const uint32_t *);
struct audio_ble_flash_callbacks {
    uintptr_t reserved;
    audio_ble_flash_control_fn control; /* native 0x20073270 + 4 */
};
extern struct audio_ble_flash_callbacks audio_ble_flash_callbacks;
uint32_t audio_ble_flash_control(uint32_t device, uint32_t enabled,
                                  const uint32_t *command) {
    if (audio_ble_flash_callbacks.control == 0) return 0u;
    return audio_ble_flash_callbacks.control((uint8_t)device,
                                             (uint8_t)enabled,command);
}
