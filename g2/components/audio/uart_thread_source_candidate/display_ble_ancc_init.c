/* Native Cordio profileAnccInit 0x4bf742. */
#include <stdint.h>
extern uint8_t audio_ble_ancc_state[]; /* RAM 0x200695c8 */
extern uint8_t audio_ble_ancc_cache[]; /* RAM 0x2006ddd4 */
extern uint8_t *audio_ble_ancc_controller; /* pointer cell 0x20074898 */
extern uint8_t *audio_ble_ancc_mode; /* pointer cell 0x2007489c */
extern uint8_t *audio_ble_ancc_service_context; /* pointer cell 0x200748a0 */
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t); /* selected 0x43c0e4 */
extern void audio_ble_ancc_reset_state_machine(void); /* native 0x4bf6c4 */
void audio_ble_profile_ancc_init(uint8_t handler,uint8_t *controller,uint8_t *mode) {
    audio_ble_ancc_state[1]=handler;
    audio_uart_buffer_zero(audio_ble_ancc_state+0x1cu,0x300u,0u);
    audio_uart_buffer_zero(audio_ble_ancc_cache,0x2fcu,0u);
    audio_ble_ancc_controller=controller;
    audio_ble_ancc_mode=mode;
    audio_ble_ancc_service_context=controller+0x30u;
    audio_ble_ancc_reset_state_machine();
}
