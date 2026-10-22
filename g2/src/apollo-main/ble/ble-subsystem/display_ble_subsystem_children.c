/* Native startup descendants 0x503b76, 0x534866, 0x532e52. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_state_20071670[];
extern uint32_t (*audio_ble_subsystem_callback_slot)(const uint8_t *); /* RAM 0x20074100 */
extern uint32_t audio_ble_subsystem_handler_503936(const uint8_t *); /* ROM Thumb 0x503937 */
extern void audio_ble_atts_csf_register(void (*)(void)); /* 0x52d4e0 */
extern void audio_ble_atts_csf_callback_53482c(void); /* ROM Thumb 0x53482d */
extern uint8_t audio_ble_subsystem_rows_200733fc[3u*0x10u];
extern uint8_t audio_ble_subsystem_link_state_200719c8[]; /* RAM 0x200719c8 */
extern uint32_t (*audio_ble_subsystem_primary_callback_slot)(const uint8_t *); /* RAM 0x200740fc */
extern uint32_t audio_ble_subsystem_primary_handler_4b3bec(const uint8_t *); /* ROM Thumb 0x4b3bed */
extern void audio_ble_subsystem_child_479418(void);
void audio_ble_subsystem_child_532e52(void) {
    for(uint32_t i=0;i<3u;i++) {
        uint8_t *row=audio_ble_subsystem_rows_200733fc+i*0x10u;
        row[0x0bu]=0u;
        *(uint32_t *)(void *)row=0u;
    }
}
void audio_ble_subsystem_child_4b32d4(void) {
    *(uint32_t *)(void *)(audio_ble_subsystem_link_state_200719c8+0x78u)=0u;
    *(uint32_t *)(void *)(audio_ble_subsystem_link_state_200719c8+0x7cu)=0u;
}
void audio_ble_subsystem_child_4b3c02(void) {
    uint8_t *state=audio_ble_subsystem_link_state_200719c8;
    for(uint32_t i=0;i<0x80u;i++) state[i]=0u;
    for(uint32_t i=0;i<2u;i++) {
        state[0x57u+i]=3u;
        state[0x59u+i]=0u;
        state[0x5bu+i]=0u;
        state[0x6au+i]=0u;
        for(uint32_t j=0;j<6u;j++) state[0x5eu+i*6u+j]=0u;
    }
    state[0x5du]=0xffu;
    audio_ble_subsystem_child_4b32d4();
    state[0x74u]=0u;
    audio_ble_subsystem_child_479418();
    audio_ble_subsystem_primary_callback_slot=audio_ble_subsystem_primary_handler_4b3bec;
}
