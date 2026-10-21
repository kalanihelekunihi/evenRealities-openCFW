/* Stock APP_MasterSetTargetAddrName entry at 0x4a2068.
 * The implementation and target storage are already owned by
 * display_ble_master_connect_children.c and display_ble_master_target_config.c. */
#include <stdint.h>

extern void audio_ble_master_set_target(const uint8_t *, const char *, uint8_t);

void audio_ble_master_set_target_hand_4a2068(const void *address,
                                              const void *name,
                                              uint32_t name_length)
{
    audio_ble_master_set_target((const uint8_t *)address,
                                (const char *)name,
                                (uint8_t)name_length);
}
