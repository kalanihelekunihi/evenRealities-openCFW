/* Native Cordio initiator/responder SMP state-machine init bodies
 * 0x537eec/0x537f14 and 0x5380dc/0x538104. */
#include <stdint.h>
extern uint8_t audio_ble_smp_handler_state[]; /* RAM 0x20070aec */
extern const uint8_t audio_ble_smpi_legacy_table[]; /* ROM 0x78c344 */
extern const uint8_t audio_ble_smpi_sc_table[]; /* ROM 0x78c320 */
extern const uint8_t audio_ble_smpr_legacy_table[]; /* ROM 0x78c4ac */
extern const uint8_t audio_ble_smpr_sc_table[]; /* ROM 0x78c470 */
extern void audio_ble_smp_pairing_callback_56e6e0(void);
extern void audio_ble_smp_auth_callback_56e84c(void);
extern void SmpScInit(void); /* native vendor child */
static void put(uint32_t offset,const void *value) {
    *(const void **)(void *)(audio_ble_smp_handler_state+offset)=value;
}
void SmpiInit(void) {
    put(0xe8u,audio_ble_smpi_legacy_table);
    put(0xf0u,audio_ble_smp_pairing_callback_56e6e0);
    put(0xf4u,audio_ble_smp_auth_callback_56e84c);
}
void SmpiScInit(void) {
    put(0xe8u,audio_ble_smpi_sc_table);
    SmpScInit();
}
void SmprInit(void) {
    put(0xe4u,audio_ble_smpr_legacy_table);
    put(0xf0u,audio_ble_smp_pairing_callback_56e6e0);
    put(0xf4u,audio_ble_smp_auth_callback_56e84c);
}
void SmprScInit(void) {
    put(0xe4u,audio_ble_smpr_sc_table);
    SmpScInit();
}
