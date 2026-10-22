/* Native 0x4bf6c4 ANCC reset and 0x4486bc OTA export reset. */
#include <stdint.h>
extern uint8_t audio_ble_ancc_state[]; /* live RAM 0x200695c8 */
extern uint8_t audio_ble_ota_export_state[]; /* live RAM 0x20072730 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void audio_ble_ota_export_mode_set(uint32_t); /* native 0x478860 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
/* Stock 0x4BF6C4 (_anccResetStateMachine) */
void audio_ble_ancc_reset_state_machine(void) {
    if(audio_log_level()&2u)
      audio_log_extended(4u,"ble.ancc",
        "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ancc\\profile_ancc.c",
        "_anccResetStateMachine",0x2ecu,"Resetting ANCS state machine");
    if((audio_log_level()&1u)||(audio_log_level()&4u))
      (void)compressed_log_output(0x10000000u,
        "[ble.ancc]Resetting ANCS state machine","[ble.ancc]Resetting ANCS state machine");
    audio_ble_ancc_state[10]=0u;
    *(uint16_t *)(void *)(audio_ble_ancc_state+0x0eu)=0u;
    *(uint16_t *)(void *)(audio_ble_ancc_state+0x0cu)=0u;
    *(uint16_t *)(void *)(audio_ble_ancc_state+0x14u)=0u;
    audio_ble_ancc_state[0x12u]=0u;
    *(uint16_t *)(void *)(audio_ble_ancc_state+0x10u)=0u;
    audio_ble_ancc_state[0x16u]=0u;
    *(uint32_t *)(void *)(audio_ble_ancc_state+0x18u)=0u;
    audio_uart_buffer_zero(audio_ble_ancc_state+0x31cu,0x40u,0u);
    audio_uart_buffer_zero(audio_ble_ancc_state+0x35cu,0x200u,0u);
}
/* Stock 0x004486BC (semantic_OtaResetExportState) */
void audio_ble_ota_reset_export_state(void) {
    audio_uart_buffer_zero(audio_ble_ota_export_state,0x60u,0u);
    audio_ble_ota_export_state[0]=0u;
    *(uint32_t *)(void *)(audio_ble_ota_export_state+0x34u)=0x2034bc10u; /* authenticated literal */
    audio_ble_ota_export_mode_set(UINT32_MAX);
}
