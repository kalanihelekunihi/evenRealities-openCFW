/* AT^TP touch-controller test command, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\eAT\at_tp.c.
 * Native 0x5a5984..0x5a5d07; literal pool 0x5a5d08..0x5a5d93.
 *
 * AT^TP=<sub>[,<arg>] for the CY8C4046FNI touch controller:
 *   1                 read the five 16-bit sensor diffs
 *   0                 reset the controller
 *   debug1 / debug0   enable / disable raw touch streaming
 *   bsln_read         read the saved proximity baseline
 *   bsln_set          reset, read version, then save the proximity baseline
 *   gesture_cfg_read  read the long-press threshold
 *   gesture_cfg_set,<ms>  write the threshold (1..65535), wait 100 ms, verify
 * Returns 1 with AT^TP+OK, or 0 after printing an error. */
#include <stdint.h>
#include "g2_at_core.h"
#include "g2_touch_cy8c4046.h"

extern volatile uint8_t g2_touch_stream_enabled;  /* RAM 0x20075017 */
extern void cy8c4046fni_reset_55b64a(void);
extern int32_t DRV_TouchReadSensorDiff_55b6a8(void *out);
extern int32_t cy8c4046fni_read_version_55b6dc(uint32_t *version);
extern uint32_t g2_log_module_length(const char *text);  /* strlen 0x44a43c */
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern int32_t audio_ble_parse_version(const char *s, const char *format, ...); /* sscanf 0x475fc0 */
extern void *g2_memset_43bb00(void *dst, int32_t value, uint32_t len);
extern int32_t osDelay(uint32_t ticks);  /* 0x449376 */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "at.tp"; /* ROM 0x78cc2c */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\eAT\\at_tp.c"; /* ROM 0x700898 */
static const char fn_test[] = "_atTpTest"; /* ROM 0x78a418 */
static const char o_gesture_cfg[] = "Gesture cfg: long_press_threshold_ms=%u\r\n"; /* ROM 0x73c560 */
static const char s_para1[] = "para1: %s"; /* ROM 0x78a424 */
static const char c_para1[] = "[at.tp]para1: %s"; /* ROM 0x77e1e0 */
static const char s_para2[] = "para2: %s"; /* ROM 0x78a430 */
static const char c_para2[] = "[at.tp]para2: %s"; /* ROM 0x77e1f4 */
static const char k_diff[] = "1"; /* ROM 0x5a5d08 */
static const char k_reset[] = "0"; /* ROM 0x5a5d0c */
static const char f_u[] = "%u"; /* ROM 0x5a5d10 */
static const char s_diff[] = "diff: %u, %u, %u, %u, %u"; /* ROM 0x769c48 */
static const char c_diff[] = "[at.tp]diff: %u, %u, %u, %u, %u"; /* ROM 0x75e250 */
static const char o_diff[] = "diff: %u, %u, %u, %u, %u\r\n"; /* ROM 0x769c64 */
static const char k_debug1[] = "debug1"; /* ROM 0x78cc34 */
static const char k_debug0[] = "debug0"; /* ROM 0x78cc3c */
static const char k_bsln_read[] = "bsln_read"; /* ROM 0x78a43c */
static const char s_bsln[] = "Proximity baseline: %u"; /* ROM 0x77562c */
static const char c_bsln[] = "[at.tp]Proximity baseline: %u"; /* ROM 0x75e270 */
static const char o_bsln[] = "Proximity baseline: %u\r\n"; /* ROM 0x769c80 */
static const char k_bsln_set[] = "bsln_set"; /* ROM 0x78a448 */
static const char s_bsln_saved[] = "Proximity baseline save command sent"; /* ROM 0x747cc4 */
static const char c_bsln_saved[] = "[at.tp]Proximity baseline save command sent"; /* ROM 0x73c58c */
static const char o_bsln_saved[] = "Proximity baseline save command sent successfully.\r\n"; /* ROM 0x71c348 */
static const char k_cfg_read[] = "gesture_cfg_read"; /* ROM 0x77e208 */
static const char o_cfg_read_failed[] = "Gesture cfg read failed.\r\n"; /* ROM 0x769c9c */
static const char k_cfg_set[] = "gesture_cfg_set"; /* ROM 0x7851c0 */
static const char o_cfg_usage[] = "Usage: AT^TP=gesture_cfg_set,<threshold_ms>\r\n"; /* ROM 0x731ba4 */
static const char o_cfg_invalid[] = "Invalid gesture cfg. Usage: AT^TP=gesture_cfg_set,<threshold_ms>\r\n"; /* ROM 0x7008dc */
static const char o_cfg_write_failed[] = "Gesture cfg write failed.\r\n"; /* ROM 0x769cb8 */
static const char o_cfg_readback_failed[] = "Gesture cfg write success, but readback failed.\r\n"; /* ROM 0x727234 */
static const char o_cfg_mismatch[] = "Gesture cfg write mismatch: wrote threshold=%u, read back threshold=%u\r\n"; /* ROM 0x6f1b90 */
static const char o_cfg_ok[] = "Gesture cfg updated and verified successfully.\r\n"; /* ROM 0x727268 */
static const char o_ok[] = "AT^TP+OK\r\n"; /* ROM 0x78a454 */

#define AT_LOG_ON() (audio_log_flags() & 2u)
#define AT_CLOG_ON() ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))

static int32_t is_cmd(const char *arg, const char *key)
{
    return audio_ble_hci_vendor_compare_44b610(arg, key, g2_log_module_length(key)) == 0;
}

void atTpPrintGestureCfg(const uint16_t *threshold)
{
    if (threshold != 0)
        at_core_output(o_gesture_cfg, (uint32_t)*threshold);
}

int32_t _atTpTest(const char *arg1, const char *arg2)
{
    if (AT_LOG_ON())
        audio_log_extended(3u, module_tag, source_file, fn_test, 0x1du, s_para1, arg1);
    if (AT_CLOG_ON())
        (void)compress_log_output(0x0c400000u, c_para1, c_para1, arg1);
    if (AT_LOG_ON())
        audio_log_extended(3u, module_tag, source_file, fn_test, 0x1eu, s_para2, arg2);
    if (AT_CLOG_ON())
        (void)compress_log_output(0x0c400000u, c_para2, c_para2, arg2);

    if (is_cmd(arg1, k_diff)) {
        uint16_t diff[5];
        (void)g2_memset_43bb00(diff, 0, sizeof diff);
        (void)DRV_TouchReadSensorDiff_55b6a8(diff);
        if (AT_LOG_ON())
            audio_log_extended(3u, module_tag, source_file, fn_test, 0x23u, s_diff, (uint32_t)diff[0],
                               (uint32_t)diff[1], (uint32_t)diff[2], (uint32_t)diff[3], (uint32_t)diff[4]);
        if (AT_CLOG_ON())
            (void)compress_log_output(0x0d400000u, c_diff, c_diff, (uint32_t)diff[0], (uint32_t)diff[1],
                                      (uint32_t)diff[2], (uint32_t)diff[3], (uint32_t)diff[4]);
        at_core_output(o_diff, (uint32_t)diff[0], (uint32_t)diff[1], (uint32_t)diff[2], (uint32_t)diff[3],
                       (uint32_t)diff[4]);
    } else if (is_cmd(arg1, k_reset)) {
        cy8c4046fni_reset_55b64a();
    } else if (is_cmd(arg1, k_debug1)) {
        g2_touch_stream_enabled = 1u;
    } else if (is_cmd(arg1, k_debug0)) {
        g2_touch_stream_enabled = 0u;
    } else if (is_cmd(arg1, k_bsln_read)) {
        uint16_t baseline = DRV_TouchReadProximityBaseline_55b78a();
        if (AT_LOG_ON())
            audio_log_extended(3u, module_tag, source_file, fn_test, 0x35u, s_bsln, (uint32_t)baseline);
        if (AT_CLOG_ON())
            (void)compress_log_output(0x0c400000u, c_bsln, c_bsln, (uint32_t)baseline);
        at_core_output(o_bsln, (uint32_t)baseline);
    } else if (is_cmd(arg1, k_bsln_set)) {
        cy8c4046fni_reset_55b64a();
        uint32_t version = 0u;
        (void)cy8c4046fni_read_version_55b6dc(&version);
        (void)DRV_TouchSaveProximityBaseline_55b730();
        if (AT_LOG_ON())
            audio_log_extended(3u, module_tag, source_file, fn_test, 0x3eu, s_bsln_saved);
        if (AT_CLOG_ON())
            (void)compress_log_output(0x0c000000u, c_bsln_saved, c_bsln_saved);
        at_core_output(o_bsln_saved);
    } else if (is_cmd(arg1, k_cfg_read)) {
        uint16_t threshold;
        (void)g2_memset_43bb00(&threshold, 0, sizeof threshold);
        if (DRV_TouchReadGestureCfg_55b92a(&threshold) != 0) {
            at_core_output(o_cfg_read_failed);
            return 0;
        }
        atTpPrintGestureCfg(&threshold);
    } else if (is_cmd(arg1, k_cfg_set)) {
        uint16_t wrote, readback;
        (void)g2_memset_43bb00(&wrote, 0, sizeof wrote);
        (void)g2_memset_43bb00(&readback, 0, sizeof readback);
        uint32_t value = 0u;
        if (arg2 == 0) {
            at_core_output(o_cfg_usage);
            return 0;
        }
        if (audio_ble_parse_version(arg2, f_u, &value) != 1 || value == 0u || value > 0xffffu) {
            at_core_output(o_cfg_invalid);
            return 0;
        }
        wrote = (uint16_t)value;
        if (DRV_TouchWriteGestureCfg_55b840(&wrote) != 0) {
            at_core_output(o_cfg_write_failed);
            return 0;
        }
        (void)osDelay(100u);
        if (DRV_TouchReadGestureCfg_55b92a(&readback) != 0) {
            at_core_output(o_cfg_readback_failed);
            return 0;
        }
        if (readback != wrote) {
            at_core_output(o_cfg_mismatch, (uint32_t)wrote, (uint32_t)readback);
            return 0;
        }
        at_core_output(o_cfg_ok);
        atTpPrintGestureCfg(&readback);
    }
    at_core_output(o_ok);
    return 1;
}
