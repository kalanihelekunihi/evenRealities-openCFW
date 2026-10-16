/* Native HAL callback table at 0x20073270: 0x3c-byte initializer clear.
 * The first two words match the existing flash-control provider's C view.
 */
#include <stdint.h>

typedef uint32_t (*audio_ble_flash_control_fn)(uint8_t, uint8_t, const uint32_t *);
struct audio_ble_flash_callbacks {
    uintptr_t reserved;
    audio_ble_flash_control_fn control;
};

struct audio_ble_flash_callbacks audio_ble_flash_callbacks
    __attribute__((section(".bss.opencfw.ble.flash.callbacks.head"), aligned(4), used));
uint8_t audio_ble_flash_callbacks_tail[0x34]
    __attribute__((section(".bss.opencfw.ble.flash.callbacks.tail"), aligned(4), used));

_Static_assert(sizeof(struct audio_ble_flash_callbacks) == 8u, "callback head ABI");
_Static_assert(sizeof(audio_ble_flash_callbacks_tail) == 0x34u, "callback tail span");
