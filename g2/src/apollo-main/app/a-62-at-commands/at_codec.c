/* AT^AUD_AUDIO test command, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\service\eAT\at_codec.c.
 * Native 0x5a5488..0x5a54fd; literal pool 0x5a5500..0x5a551f.
 *
 * "1" acquires the audio path for audio-manager user 7, "0" releases it;
 * any other argument only logs. Always replies AUD_AUDIO+OK. */
#include <stdint.h>
#include "g2_at_core.h"

#define AUDIO_USER_AT 7u

extern int32_t AUDM_appAcquire(uint32_t user);  /* 0x54f380 */
extern int32_t AUDM_appRelease(uint32_t user);  /* 0x54f50e */
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *a, const void *b, uint32_t len); /* strncmp */
extern uint32_t audio_log_flags(void); /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...); /* 0x43ce9e */

static const char module_tag[] = "at.codec"; /* ROM 0x78a340 */
static const char source_file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\eAT\\at_codec.c"; /* ROM 0x700810 */
static const char fn_audio_ctrl[] = "_atAudioCtrl"; /* ROM 0x785120 */
static const char s_set_audio[] = "set audio %s"; /* ROM 0x785130 */
static const char c_set_audio[] = "[at.codec]set audio %s"; /* ROM 0x7755b4 */
static const char k_on[] = "1"; /* ROM 0x5a5500 */
static const char k_off[] = "0"; /* ROM 0x5a5504 */
static const char o_ok[] = "AUD_AUDIO+OK\r\n"; /* ROM 0x785140 */

int32_t _atAudioCtrl(const char *arg1, const char *arg2)
{
    (void)arg2;
    if (audio_log_flags() & 2u)
        audio_log_extended(3u, module_tag, source_file, fn_audio_ctrl, 0x0eu, s_set_audio, arg1);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compress_log_output(0x0c400000u, c_set_audio, c_set_audio, arg1);
    if (audio_ble_hci_vendor_compare_44b610(arg1, k_on, 1u) == 0)
        (void)AUDM_appAcquire(AUDIO_USER_AT);
    else if (audio_ble_hci_vendor_compare_44b610(arg1, k_off, 1u) == 0)
        (void)AUDM_appRelease(AUDIO_USER_AT);
    at_core_output(o_ok);
    return 1;
}
