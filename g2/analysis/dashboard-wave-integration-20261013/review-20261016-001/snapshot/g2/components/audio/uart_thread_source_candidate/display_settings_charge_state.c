/* Native CHG_GetSoc 0x4ad8fa and CHG_GetIsCharging 0x4ad900. */
#include <stdint.h>
extern uint8_t audio_charger_state[]; /* live RAM 0x20073b30, at least 0x15 bytes */
uint32_t audio_settings_charge_percent(void) {
    return *(const uint32_t *)(const void *)(audio_charger_state+0x10u);
}
int32_t audio_settings_is_charging(void) {
    return *(const int8_t *)(const void *)(audio_charger_state+0x14u);
}
