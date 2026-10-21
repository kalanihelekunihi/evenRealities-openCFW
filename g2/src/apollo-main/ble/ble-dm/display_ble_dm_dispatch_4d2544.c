/* Native 0x4d2544 forwards directly to SmpDbInit at 0x542288. */
extern void SmpDbInit(void);

void audio_ble_dm_dispatch_4d2544(void *message)
{
    (void)message;
    SmpDbInit();
}
