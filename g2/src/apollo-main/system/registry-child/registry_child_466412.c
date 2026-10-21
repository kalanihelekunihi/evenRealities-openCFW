/* Stock Apollo 0x466412: universal setting sync receive handler. */
#include <stdint.h>

extern uint8_t audio_uart_hand_record[0x30u]; /* 0x4667ec -> 0x200736d4 */
extern uint8_t audio_uart_device_role_get(void); /* selected 0x45a568 */
extern void *audio_queue_copy_bytes(void *, const void *, uint32_t); /* selected 0x439be4 */
extern uint32_t audio_uart_registry_hand_compare_46636c(const uint8_t *);
extern void audio_uart_ring_unpair_publish_hand_4661a6(void);
extern uint32_t audio_log_flags(void); /* selected 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...); /* selected 0x43d574 */
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "srv_universal_setting";
static const char path[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\service_universal_setting\\service_universal_setting.c";
static const char function[] = "svc_universal_setting_sync_handler";
static const char same[] = "universal_setting all values match, not send";
static const char same_short[] = "[srv_universal_setting]universal_setting all values match, not send";
static const char different[] = "Recv slave universal setting sync, values not match, send config to slave";
static const char different_short[] = "[srv_universal_setting]Recv slave universal setting sync, values not match, send config to slave";

static void log_result(uint32_t line, const char *message, const char *short_message) {
    if((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, function, line, message);
    if((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compressed_log_output(0x0c000000u, short_message, short_message);
}

void audio_uart_registry_child_466412(uint32_t payload, uint32_t length) {
    const uint8_t *record = (const uint8_t *)(uintptr_t)payload;
    (void)length;
    if(record[0] == 0u && audio_uart_device_role_get() == 2u) {
        (void)audio_queue_copy_bytes(audio_uart_hand_record, record + 2u, 20u);
        (void)audio_queue_copy_bytes(audio_uart_hand_record + 20u, record + 24u, 12u);
        (void)audio_queue_copy_bytes(audio_uart_hand_record + 32u, record + 36u, 12u);
        return;
    }
    if(record[0] != 1u || audio_uart_device_role_get() != 1u) return;
    if(audio_uart_registry_hand_compare_46636c(record) != 0u) {
        log_result(0xefu, same, same_short);
        return;
    }
    log_result(0xf2u, different, different_short);
    audio_uart_ring_unpair_publish_hand_4661a6();
}
