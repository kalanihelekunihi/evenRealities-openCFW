/* SVC_ANCC deinit, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\message_notify\service_ancc.c.
 * Stock range 0x49739e..0x4973f3 (literal pool entries 0x497938, 0x497958,
 * 0x49795c, 0x497d24). Sibling functions of this TU are in
 * app/a-15-ancc-service/service_ancc.c.
 *
 * Under the ANCC message mutex it clears the ten 0x304-byte notification
 * records, the in-use list head and the record count; it then deletes the
 * mutex and tears down the message-count callback list. */
#include <stdint.h>

extern void *audio_settings_ancc_mutex;                     /* RAM 0x2007491c */
extern uint8_t audio_settings_ancc_count;                   /* RAM 0x2007500d */
extern uint8_t g2_audio_ancc_records_20104c54[0x1e28];      /* RAM 0x20104c54 */
extern uint32_t g2_audio_ancc_sequence_20074918;            /* RAM 0x20074918, list head */

extern int32_t osMutexAcquire(void *mutex, uint32_t timeout); /* 0x4497b6 */
extern int32_t osMutexRelease(void *mutex);                 /* 0x44981c */
extern int32_t osMutexDelete(void *mutex);                  /* 0x44986e */
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void CB_ANCC_DeinitMsgCountCallbacks(void);          /* 0x4e1a54 */

/* Stock 0x0049739E (service_ancc_deinit_49739e) */
void service_ancc_deinit_49739e(void)
{
    if (audio_settings_ancc_mutex != 0 &&
        osMutexAcquire(audio_settings_ancc_mutex, 0xffffffffu) == 0) {
        audio_uart_buffer_zero(g2_audio_ancc_records_20104c54, 0x1e28u, 0u);
        g2_audio_ancc_sequence_20074918 = 0u;
        audio_settings_ancc_count = 0u;
        (void)osMutexRelease(audio_settings_ancc_mutex);
    }
    if (audio_settings_ancc_mutex != 0) {
        (void)osMutexDelete(audio_settings_ancc_mutex);
        audio_settings_ancc_mutex = 0;
    }
    CB_ANCC_DeinitMsgCountCallbacks();
}
