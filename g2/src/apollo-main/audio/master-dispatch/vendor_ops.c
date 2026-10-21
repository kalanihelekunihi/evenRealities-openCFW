#include <stdint.h>

extern void *WsfMsgAlloc(uint16_t);
extern void WsfMsgSend(uint8_t, void *);
extern void SmpDmMsgSend(void *);
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t);
extern uint8_t audio_ble_dm_handler_state[];

/* Native 0x55bbea: prepare the eight-byte SMP link start message. */
void audio_ble_vendor_link_start_55bbea(uint32_t connection, uint32_t mode,
                                        uint32_t profile, uint32_t options,
                                        uint32_t flags)
{
    volatile uint8_t *message = (volatile uint8_t *)WsfMsgAlloc(8u);
    if (message == 0)
        return;
    message[2] = 1u;
    *(volatile uint16_t *)message = (uint8_t)connection;
    message[4] = (uint8_t)mode;
    message[5] = (uint8_t)profile;
    message[6] = (uint8_t)(options & 7u);
    message[7] = (uint8_t)(flags & 7u);
    SmpDmMsgSend((void *)message);
}

/* Native 0x55bc1e: package a selected 26-byte link descriptor. */
void audio_ble_vendor_link_activate_55bc1e(uint32_t connection,
                                            uint32_t selected,
                                            uint32_t descriptor)
{
    volatile uint8_t *message = (volatile uint8_t *)WsfMsgAlloc(32u);
    if (message == 0)
        return;
    message[2] = 0x28u;
    *(volatile uint16_t *)message = (uint8_t)connection;
    (void)audio_queue_copy_bytes((void *)(message + 4),
                                 (const void *)(uintptr_t)descriptor, 26u);
    message[30] = (uint8_t)selected;
    WsfMsgSend(audio_ble_dm_handler_state[12], (void *)message);
}
