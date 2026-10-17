/* Cordio ATT callback interfaces, stock ROM 0x785250/0x7852c0/0x7852f0.
 * Field order follows the pinned Cordio attc_main.c, atts_ind.c and
 * atts_main.c attFcnIf_t initializers. ABI declarations below establish
 * address relocations; callback argument contracts belong to each body. */
#include <stdint.h>

extern void audio_ble_att_noop_4b4eec(void);
extern void audio_ble_attc_data_53119c(void);
extern void audio_ble_attc_ctrl_531330(void);
extern void audio_ble_attc_msg_5315b4(void);
extern void audio_ble_attc_conn_53135a(void);
extern void audio_ble_atts_ind_ctrl_533c4c(void);
extern void audio_ble_atts_ind_msg_533bcc(void);
extern void audio_ble_atts_ind_conn_533a40(void);
extern void audio_ble_atts_data_53498c(void);
extern void audio_ble_atts_ctrl_534c8a(void);
extern void audio_ble_atts_msg_534c42(void);
extern void audio_ble_atts_conn_534aba(void);

const uintptr_t audio_ble_attc_table[4] = {
    (uintptr_t)&audio_ble_attc_data_53119c,
    (uintptr_t)&audio_ble_attc_ctrl_531330,
    (uintptr_t)&audio_ble_attc_msg_5315b4,
    (uintptr_t)&audio_ble_attc_conn_53135a,
};
const uintptr_t audio_ble_atts_ind_table[4] = {
    (uintptr_t)&audio_ble_att_noop_4b4eec,
    (uintptr_t)&audio_ble_atts_ind_ctrl_533c4c,
    (uintptr_t)&audio_ble_atts_ind_msg_533bcc,
    (uintptr_t)&audio_ble_atts_ind_conn_533a40,
};
const uintptr_t audio_ble_atts_table[4] = {
    (uintptr_t)&audio_ble_atts_data_53498c,
    (uintptr_t)&audio_ble_atts_ctrl_534c8a,
    (uintptr_t)&audio_ble_atts_msg_534c42,
    (uintptr_t)&audio_ble_atts_conn_534aba,
};
_Static_assert(sizeof(audio_ble_attc_table) == 16u, "Cordio ATT client ABI");
_Static_assert(sizeof(audio_ble_atts_ind_table) == 16u,
               "Cordio ATT indication ABI");
_Static_assert(sizeof(audio_ble_atts_table) == 16u, "Cordio ATT server ABI");
