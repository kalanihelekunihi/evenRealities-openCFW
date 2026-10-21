/* Apollo master event leaves 0x50366e, 0x5037bc, 0x5037c4, 0x5037d0. */
#include <stdint.h>

extern volatile uint8_t audio_ble_subsystem_state_20071670[];
extern void audio_ble_master_child_503540(uint8_t,void *);
extern void audio_ble_master_child_503568(void *,void *);
extern void audio_ble_master_child_4bb25c(uint8_t);
extern void audio_ble_master_child_4bb21c(uint32_t);

void audio_ble_master_event_50366e(void *message,void *record)
{
    uint8_t status=((const uint8_t *)message)[3];
    if (status==0u)
        audio_ble_master_child_503540(status,record);
}

void audio_ble_master_event_5037bc(void *message,void *record)
{
    audio_ble_master_child_503568(message,record);
}

void audio_ble_master_event_5037c4(void *message,void *record)
{
    (void)record;
    audio_ble_master_child_4bb25c(((const uint8_t *)message)[0]);
}

void audio_ble_master_event_5037d0(void *message,void *record)
{
    (void)message;
    uint8_t *row=(uint8_t *)record;
    uint32_t handle=*(const uint32_t *)(const void *)row;
    audio_ble_master_child_4bb21c(handle);
    row[4]=0u;
    audio_ble_subsystem_state_20071670[0x9cu]=0u;
}
