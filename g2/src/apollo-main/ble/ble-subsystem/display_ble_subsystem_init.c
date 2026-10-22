/* Native bleSubsystemInit 0x4b7478, ordered application manager setup. */
extern void audio_ble_subsystem_child_503b76(void);
extern void audio_ble_subsystem_child_4b3c02(void);
extern void audio_ble_subsystem_child_534866(void);
extern void audio_ble_subsystem_child_532e52(void);
/* Stock 0x4B7478 (bleSubsystemInit) */
void audio_ble_subsystem_init(void) {
    audio_ble_subsystem_child_503b76();
    audio_ble_subsystem_child_4b3c02();
    audio_ble_subsystem_child_534866();
    audio_ble_subsystem_child_532e52();
}
