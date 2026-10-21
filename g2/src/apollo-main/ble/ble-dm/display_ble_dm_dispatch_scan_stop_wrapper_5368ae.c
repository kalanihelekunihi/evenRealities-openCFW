/* Native 0x5368ae forwards directly to the Cordio scan-stop action. */
extern void audio_ble_dm_dispatch_536896(void *);

void audio_ble_dm_dispatch_5368ae(void *message)
{
    audio_ble_dm_dispatch_536896(message);
}
