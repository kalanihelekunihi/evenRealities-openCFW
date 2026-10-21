/* Apollo BLE master connection-row reset 0x503540. */
#include <stdint.h>

extern volatile uint8_t audio_ble_subsystem_state_20071670[];

void audio_ble_master_child_503540(uint8_t status,void *record)
{
    (void)status;
    (void)record;
    audio_ble_subsystem_state_20071670[0x96u]=0u;
    for (unsigned row=0;row<10u;++row)
        audio_ble_subsystem_state_20071670[row*0x0fu+6u]=0xffu;
    audio_ble_subsystem_state_20071670[0x9cu]=0u;
}
