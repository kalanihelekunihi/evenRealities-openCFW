/* Apollo master address-layout mode getter 0x536a00. */
#include <stdint.h>

extern volatile uint8_t audio_ble_mode_runtime_20000694[];
extern const uint8_t audio_ble_dm_stack_table_78a88c[];

uint32_t audio_ble_master_mode_get_536a00(void)
{
    uint32_t selected=*(const volatile uint32_t *)(const void *)
        (audio_ble_mode_runtime_20000694+8u);
    return selected==(uint32_t)(uintptr_t)audio_ble_dm_stack_table_78a88c;
}
