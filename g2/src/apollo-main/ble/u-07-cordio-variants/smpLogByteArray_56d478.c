/* Packetcraft Cordio SMP, smpLogByteArray() as built for G2.
 * Stock source: D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\
 *               ble-host\sources\stack\smp\smp_sc_main.c
 * Native 0x56d478..0x56d812; literal pool 0x56d82c..0x56d840, 0x56d8c0.
 *
 * The C text matches upstream r20.05c (both SMP_TRACE_INFO0 calls are at the
 * upstream lines 711 and 746, built with WSF_TRACE_ENABLED); the difference
 * is the product WSF-trace macro, which expands each SMP_TRACE_INFO0 into
 * the elog level dispatch below instead of a plain WsfTrace call. The
 * upstream quirks are kept: a final chunk shorter than 16 bytes uses
 * count = j (so a len < 16 call never advances and repeats "[]" forever),
 * and the trailing "if (pos)" block is unreachable (IAR dropped it). */
#include <stdint.h>

extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *a, const char *b, uint32_t count); /* 0x44b610 */
extern void audio_ble_wsf_trace(const char *level, ...);                      /* WsfTrace 0x52a63c */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t level, const char *tag, const char *path, const char *function,
                               uint32_t line, const char *format, ...);

static const char s_err[] = "ERR";   /* ROM 0x56d760 */
static const char s_warn[] = "WARN"; /* ROM 0x78e714 */
static const char s_info[] = "INFO"; /* ROM 0x78e70c */
static const char s_smp[] = "SMP";   /* ROM 0x56d6c8 (a second copy at 0x56d818 feeds one level-3 call) */
static const char s_hci[] = "HCI";   /* ROM 0x56d814 */
static const char s_path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\stack\\smp\\smp_sc_main.c"; /* ROM 0x6de8b4 */
static const char s_function[] = "smpLogByteArray"; /* ROM 0x789190 */

/* SMP_TRACE_INFO0(text): the text itself is the format string. */
static void smp_trace_info0(const char *text, uint32_t line)
{
    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
        audio_l2c_strncmp(s_info, s_err, 3u) != 0) {
        if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
            audio_l2c_strncmp(s_info, s_warn, 4u) != 0) {
            if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                audio_l2c_strncmp(s_info, s_info, 4u) != 0) {
                if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u) {
                    if (audio_ble_hci_vendor_log_enabled_4c9c50() == 0u ||
                        audio_l2c_strncmp(s_smp, s_hci, 3u) != 0)
                        audio_ble_wsf_trace(s_info, text);
                } else if ((audio_log_flags() & 2u) != 0u) {
                    audio_log_extended(4u, s_smp, s_path, s_function, line, text);
                }
            } else if ((audio_log_flags() & 2u) != 0u) {
                audio_log_extended(3u, s_smp, s_path, s_function, line, text);
            }
        } else if ((audio_log_flags() & 2u) != 0u) {
            audio_log_extended(2u, s_smp, s_path, s_function, line, text);
        }
    } else if ((audio_log_flags() & 2u) != 0u) {
        audio_log_extended(1u, s_smp, s_path, s_function, line, text);
    }
}

void smpLogByteArray_56d478(char *str, uint8_t *pArray, uint8_t len)
{
    char buffer[512];
    int32_t j = 0;
    int32_t pos = 0;

    smp_trace_info0(str, 711u);

    while (j < (int32_t)len) {
        int32_t count = 16;
        if ((int32_t)len - j < count)
            count = j;

        buffer[pos++] = '[';
        for (int32_t i = 0; i < count; i++, j++) {
            uint8_t quad;
            if (i != 0 && (i & 3) == 0)
                buffer[pos++] = ' ';
            quad = (uint8_t)(pArray[j] >> 4);
            buffer[pos++] = (char)(quad < 10u ? '0' + quad : 'a' + quad - 10u);
            quad = (uint8_t)(pArray[j] & 0x0fu);
            buffer[pos++] = (char)(quad < 10u ? '0' + quad : 'a' + quad - 10u);
        }
        buffer[pos++] = ']';
        buffer[pos++] = '\0';
        smp_trace_info0(buffer, 746u);
        pos = 0;
    }
}
