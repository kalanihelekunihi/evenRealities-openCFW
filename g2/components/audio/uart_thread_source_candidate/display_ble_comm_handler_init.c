/* Native bleCommHandlerInit 0x4b7e74, including ordered profile setup. */
#include <stdint.h>
extern uint8_t audio_ble_comm_state[]; /* live RAM base 0x200727f0 */
extern const uint8_t audio_ble_comm_registration_table[]; /* ROM 0x774d44 */
extern const uint8_t audio_ble_comm_profile_table[]; /* ROM 0x78c9a4 */
extern const uint8_t *audio_ble_comm_registration_slot; /* RAM 0x200004b8 */
extern const uint8_t *audio_ble_comm_profile_slot; /* RAM 0x20074358 */
extern uint8_t audio_ble_comm_mode; /* RAM 0x200737b0 */
extern void audio_ble_app_slave_handler_init(uint8_t,uint8_t *,uint8_t *); /* 0x46ed94 */
extern void audio_ble_profile_handler_init(uint8_t,uint8_t *,uint8_t *); /* 0x535488 */
extern void audio_ble_app_master_handler_init(uint8_t,uint8_t *,uint8_t *); /* 0x4a19f4 */
extern void audio_ble_subsystem_init(void); /* 0x4b7478 */
void audio_ble_comm_handler_init(uint8_t handler) {
    audio_ble_comm_state[0x56u]=handler;
    audio_ble_comm_registration_slot=audio_ble_comm_registration_table;
    audio_ble_comm_profile_slot=audio_ble_comm_profile_table;
    audio_ble_comm_mode=4u;
    audio_ble_app_slave_handler_init(handler,audio_ble_comm_state,&audio_ble_comm_mode);
    audio_ble_profile_handler_init(handler,audio_ble_comm_state,&audio_ble_comm_mode);
    audio_ble_app_master_handler_init(handler,audio_ble_comm_state,&audio_ble_comm_mode);
    audio_ble_subsystem_init();
}
