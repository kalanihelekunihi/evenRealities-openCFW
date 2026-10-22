/* AT^BUZZER test command, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\eAT\at_buzzer.c.
 * Native 0x5a4fd0..0x5a53c5; literal pool 0x5a53c8..0x5a5487.
 *
 * AT^BUZZER=note,<note 0-7>,<tone 0-3>,<beat 1-100> | play,<type 0-10> |
 * start,<freq 1-20000>,<duty 0-100> | stop. Returns 1 when a subcommand ran,
 * 0 on usage or parameter errors. */
#include <stddef.h>
#include <stdint.h>
#include "g2_buzzer.h"

extern void at_core_output(const char *fmt, ...);
extern void DRV_BuzzerPlay(uint32_t type); /* 0x502bf0, defined as audio_wear_child_502bf0 */
extern char *strchr_481818(const char *s, int32_t c);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern void *audio_settings_copy_text(void *dst, const void *src, uint32_t len); /* 0x44b5a0 strncpy */
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern int32_t audio_ble_parse_version(const char *s, const char *fmt, ...); /* 0x475fc0 sscanf */
extern int32_t atoi_48d868(const char *s);
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "at.buzzer"; /* ROM 0x78a304 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\eAT\\at_buzzer.c"; /* ROM 0x6f87ec */
static const char fn_test[] = "_atBuzzerTest"; /* ROM 0x7850f0 */
static const char s_null[] = "NULL"; /* ROM 0x78cb8c */
static const char s_para1[] = "AT^BUZZER: para1=%s"; /* ROM 0x77e190 */
static const char c_para1[] = "[at.buzzer]AT^BUZZER: para1=%s"; /* ROM 0x75e130 */
static const char o_missing[] = "AT^BUZZER: Missing parameters\r\n"; /* ROM 0x75e150 */
static const char o_usage[] = "Usage:\r\n"; /* ROM 0x78a310 */
static const char o_usage_note[] = "  AT^BUZZER=note,<note>,<tone>,<beat>\r\n"; /* ROM 0x747b5c */
static const char o_usage_play[] = "  AT^BUZZER=play,<type>\r\n"; /* ROM 0x769b14 */
static const char o_usage_start[] = "  AT^BUZZER=start,<freq>,<duty>\r\n"; /* ROM 0x7522e0 */
static const char o_usage_stop[] = "  AT^BUZZER=stop\r\n"; /* ROM 0x77e1a4 */
static const char s_subcmd[] = "subcmd=%s, params=%s"; /* ROM 0x775554 */
static const char c_subcmd[] = "[at.buzzer]subcmd=%s, params=%s"; /* ROM 0x75e170 */
static const char k_note[] = "note"; /* ROM 0x78cb94 */
static const char o_note_missing[] = "AT^BUZZER=note: Missing parameters\r\n"; /* ROM 0x747b84 */
static const char o_note_usage[] = "Usage: AT^BUZZER=note,<note>,<tone>,<beat>\r\n"; /* ROM 0x731b14 */
static const char f_three[] = "%d,%d,%d"; /* ROM 0x78a31c */
static const char o_note_invalid[] = "AT^BUZZER=note: Invalid parameters (parsed %d)\r\n"; /* ROM 0x727164 */
static const char s_note[] = "Buzzer note: note=%d, tone=%d, beat=%d"; /* ROM 0x747bac */
static const char c_note[] = "[at.buzzer]Buzzer note: note=%d, tone=%d, beat=%d"; /* ROM 0x727198 */
static const char o_note[] = "Buzzer note: %d, tone: %d, beat: %d\r\n"; /* ROM 0x747bd4 */
static const char o_ok[] = "AT^BUZZER+OK\r\n"; /* ROM 0x785100 */
static const char o_note_range[] = "AT^BUZZER=note: Parameters out of range\r\n"; /* ROM 0x73c4b0 */
static const char o_note_limits[] = "note: 0-7, tone: 0-3, beat: 1-100\r\n"; /* ROM 0x752304 */
static const char k_play[] = "play"; /* ROM 0x78cb9c */
static const char o_play_missing[] = "AT^BUZZER=play: Missing parameter\r\n"; /* ROM 0x752328 */
static const char o_play_usage[] = "Usage: AT^BUZZER=play,<type>\r\n"; /* ROM 0x75e190 */
static const char o_play_range[] = "AT^BUZZER=play: Type out of range (0-10)\r\n"; /* ROM 0x73c4dc */
static const char s_play[] = "Buzzer play type: %d"; /* ROM 0x77556c */
static const char c_play[] = "[at.buzzer]Buzzer play type: %d"; /* ROM 0x75e1b0 */
static const char o_play[] = "Buzzer play type: %d\r\n"; /* ROM 0x775584 */
static const char k_start[] = "start"; /* ROM 0x78cba4 */
static const char o_start_missing[] = "AT^BUZZER=start: Missing parameters\r\n"; /* ROM 0x747bfc */
static const char o_start_usage[] = "Usage: AT^BUZZER=start,<freq>,<duty>\r\n"; /* ROM 0x747c24 */
static const char f_two[] = "%d,%d"; /* ROM 0x78cbac */
static const char o_start_invalid[] = "AT^BUZZER=start: Invalid parameters (parsed %d)\r\n"; /* ROM 0x7271cc */
static const char o_start_range[] = "AT^BUZZER=start: Parameters out of range\r\n"; /* ROM 0x73c508 */
static const char o_start_limits[] = "freq: 1-20000, duty: 0-100\r\n"; /* ROM 0x75e1d0 */
static const char s_start[] = "Buzzer start: freq=%d, duty=%d"; /* ROM 0x75e1f0 */
static const char c_start[] = "[at.buzzer]Buzzer start: freq=%d, duty=%d"; /* ROM 0x73c534 */
static const char o_start[] = "Buzzer start: freq=%d, duty=%d\r\n"; /* ROM 0x75234c */
static const char k_stop[] = "stop"; /* ROM 0x78cbb4 */
static const char s_stop[] = "Buzzer stop"; /* ROM 0x78a328 */
static const char c_stop[] = "[at.buzzer]Buzzer stop"; /* ROM 0x77559c */
static const char o_stop[] = "Buzzer stop\r\n"; /* ROM 0x785110 */
static const char o_unknown[] = "AT^BUZZER: Unknown subcommand '%s'\r\n"; /* ROM 0x747c4c */
static const char o_use[] = "Use: note, play, start, stop\r\n"; /* ROM 0x75e210 */

#define AT_LOG_ON()  (audio_log_flags() & 2u)
#define AT_CLOG_ON() ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))

int32_t _atBuzzerTest(const char *para1) {
    if (AT_LOG_ON())
        audio_log_extended(3u, module_tag, source_file, fn_test, 0x25u, s_para1, para1 != NULL ? para1 : s_null);
    if (AT_CLOG_ON())
        (void)compress_log_output(0x0c400000u, c_para1, c_para1, para1 != NULL ? para1 : s_null);
    if (para1 == NULL) {
        at_core_output(o_missing);
        at_core_output(o_usage);
        at_core_output(o_usage_note);
        at_core_output(o_usage_play);
        at_core_output(o_usage_start);
        at_core_output(o_usage_stop);
        return 0;
    }

    /* Split "<subcmd>,<params>"; the subcommand is cut to 15 characters. */
    const char *comma = strchr_481818(para1, ',');
    char subcmd[16];
    const char *params;
    audio_uart_buffer_zero(subcmd, sizeof(subcmd), 0u);
    if (comma == NULL) {
        (void)audio_settings_copy_text(subcmd, para1, 15u);
        params = NULL;
    } else {
        uint32_t len = (uint32_t)(comma - para1);
        if (len > 15u)
            len = 15u;
        (void)audio_settings_copy_text(subcmd, para1, len);
        subcmd[len] = '\0';
        params = comma + 1;
    }
    if (AT_LOG_ON())
        audio_log_extended(4u, module_tag, source_file, fn_test, 0x4au, s_subcmd, subcmd,
                           params != NULL ? params : s_null);
    if (AT_CLOG_ON())
        (void)compress_log_output(0x10800000u, c_subcmd, c_subcmd, subcmd, params != NULL ? params : s_null);

    if (audio_ble_hci_vendor_compare_44b610(subcmd, k_note, 4u) == 0) {
        if (params == NULL) {
            at_core_output(o_note_missing);
            at_core_output(o_note_usage);
            return 0;
        }
        uint32_t note = 0u, tone = 0u, beat = 0u;
        int32_t parsed = audio_ble_parse_version(params, f_three, &note, &tone, &beat);
        if (parsed != 3) {
            at_core_output(o_note_invalid, parsed);
            at_core_output(o_note_usage);
            return 0;
        }
        if (note > 7u || tone > 3u || beat - 1u > 99u) {
            at_core_output(o_note_range);
            at_core_output(o_note_limits);
            return 0;
        }
        if (AT_LOG_ON())
            audio_log_extended(3u, module_tag, source_file, fn_test, 99u, s_note, note, tone, beat);
        if (AT_CLOG_ON())
            (void)compress_log_output(0x0cc00000u, c_note, c_note, note, tone, beat);
        at_core_output(o_note, note, tone, beat);
        DRV_BuzzerPlayNote((uint8_t)note, (uint8_t)tone, (uint8_t)beat);
        at_core_output(o_ok);
    } else if (audio_ble_hci_vendor_compare_44b610(subcmd, k_play, 4u) == 0) {
        if (params == NULL) {
            at_core_output(o_play_missing);
            at_core_output(o_play_usage);
            return 0;
        }
        uint32_t type = (uint32_t)atoi_48d868(params);
        if (type > 10u) {
            at_core_output(o_play_range);
            return 0;
        }
        if (AT_LOG_ON())
            audio_log_extended(3u, module_tag, source_file, fn_test, 0x83u, s_play, type);
        if (AT_CLOG_ON())
            (void)compress_log_output(0x0c400000u, c_play, c_play, type);
        at_core_output(o_play, type);
        DRV_BuzzerPlay(type);
        at_core_output(o_ok);
    } else if (audio_ble_hci_vendor_compare_44b610(subcmd, k_start, 5u) == 0) {
        if (params == NULL) {
            at_core_output(o_start_missing);
            at_core_output(o_start_usage);
            return 0;
        }
        int32_t freq = 0;
        uint32_t duty = 0u;
        int32_t parsed = audio_ble_parse_version(params, f_two, &freq, &duty);
        if (parsed != 2) {
            at_core_output(o_start_invalid, parsed);
            at_core_output(o_start_usage);
            return 0;
        }
        if ((uint32_t)freq - 1u > 19999u || duty > 100u) {
            at_core_output(o_start_range);
            at_core_output(o_start_limits);
            return 0;
        }
        if (AT_LOG_ON())
            audio_log_extended(3u, module_tag, source_file, fn_test, 0xa5u, s_start, freq, duty);
        if (AT_CLOG_ON())
            (void)compress_log_output(0x0c800000u, c_start, c_start, freq, duty);
        at_core_output(o_start, freq, duty);
        DRV_BuzzerStart((uint32_t)freq, (uint8_t)duty);
        at_core_output(o_ok);
    } else if (audio_ble_hci_vendor_compare_44b610(subcmd, k_stop, 4u) == 0) {
        if (AT_LOG_ON())
            audio_log_extended(3u, module_tag, source_file, fn_test, 0xaeu, s_stop);
        if (AT_CLOG_ON())
            (void)compress_log_output(0x0c000000u, c_stop, c_stop);
        at_core_output(o_stop);
        DRV_BuzzerStop();
        at_core_output(o_ok);
    } else {
        at_core_output(o_unknown, subcmd);
        at_core_output(o_use);
        return 0;
    }
    return 1;
}
