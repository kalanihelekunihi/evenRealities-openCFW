/* GX8002 service wrappers, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_codec_host.c.
 * Native SVC_SwitchBFMode 0x57d418, SVC_SwitchWakeupMode 0x57d4e4,
 * SVC_SetMicGain 0x57d5c0, SVC_CodecMicDelay1Bit 0x57d870; literal pool
 * 0x57db98..0x57dc0f. (SVC_CodecDMICOpen/Close and SVC_I2SOutputCtrl are
 * reconstructed in system/glue/dsp_control_provider.c.)
 *
 * Each wrapper uses the 200-tick timeout and checks the codec status byte.
 * Stock quirk: only SVC_SetMicGain maps "transport ok, bad status" to -1;
 * the other three return the transport status, i.e. 0, in that case. */
#include <stdint.h>
#include "gx8002_host.h"

static const char module[] = "codec.host"; /* ROM 0x78bed0 */
static const char file[] = "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_codec_host.c"; /* ROM 0x6fccd4 */

static const char fn_bf[] = "SVC_SwitchBFMode"; /* ROM 0x7830b4 */
static const char bf_fail[] = "SwitchBFMode failed: %d, response status: 0x%02X"; /* ROM 0x72d248 */
static const char bf_fail_s[] = "[codec.host]SwitchBFMode failed: %d, response status: 0x%02X"; /* ROM 0x70eb24 */
static const char bf_ok[] = "SwitchBFMode success"; /* ROM 0x77b6bc */
static const char bf_ok_s[] = "[codec.host]SwitchBFMode success"; /* ROM 0x759870 */

static const char fn_wakeup[] = "SVC_SwitchWakeupMode"; /* ROM 0x77b6d4 */
static const char wakeup_fail[] = "SwitchWakeupMode failed: %d, response status: 0x%02X"; /* ROM 0x722a88 */
static const char wakeup_fail_s[] = "[codec.host]SwitchWakeupMode failed: %d, response status: 0x%02X"; /* ROM 0x705804 */
static const char wakeup_ok[] = "SwitchWakeupMode success"; /* ROM 0x7710e0 */
static const char wakeup_ok_s[] = "[codec.host]SwitchWakeupMode success"; /* ROM 0x74dc8c */

static const char fn_gain[] = "SVC_SetMicGain"; /* ROM 0x7888b0 */
static const char gain_fail[] = "SetMicGain failed: %d, rsp=0x%04X"; /* ROM 0x759894 */
static const char gain_fail_s[] = "[codec.host]SetMicGain failed: %d, rsp=0x%04X"; /* ROM 0x738294 */
static const char gain_ok[] = "SetMicGain success, gain=%u"; /* ROM 0x7710fc */
static const char gain_ok_s[] = "[codec.host]SetMicGain success, gain=%u"; /* ROM 0x74dcb4 */

static const char fn_delay[] = "SVC_CodecMicDelay1Bit"; /* ROM 0x77b6ec */
static const char delay_fail[] = "CodecMicDelay1Bit failed: %d, response status: 0x%02X"; /* ROM 0x722ac0 */
static const char delay_fail_s[] = "[codec.host]CodecMicDelay1Bit failed: %d, response status: 0x%02X"; /* ROM 0x705848 */
static const char delay_ok[] = "CodecMicDelay1Bit success"; /* ROM 0x771118 */
static const char delay_ok_s[] = "[codec.host]CodecMicDelay1Bit success"; /* ROM 0x74dcdc */

/* Success requires codec status 1. */
int32_t SVC_SwitchBFMode(void)
{
    uint8_t response;
    int32_t status;

    audio_uart_buffer_zero(&response, 1u, 0u);
    status = GX8002_SwitchBFMode(&response, GX8002_SVC_TIMEOUT);
    if (status == 0 && response == 1u) {
        GX8002_LOG(3u, 0x0c000000u, fn_bf, 758u, bf_ok, bf_ok_s);
        return 0;
    }
    GX8002_LOG(1u, 0x04800000u, fn_bf, 755u, bf_fail, bf_fail_s, status, response);
    return status;
}

/* Success requires codec status 0 (the image-B handler always answers 0). */
int32_t SVC_SwitchWakeupMode(void)
{
    uint8_t response;
    int32_t status;

    audio_uart_buffer_zero(&response, 1u, 0u);
    status = GX8002_SwitchWakeupMode(&response, GX8002_SVC_TIMEOUT);
    if (status == 0 && response == 0u) {
        GX8002_LOG(3u, 0x0c000000u, fn_wakeup, 774u, wakeup_ok, wakeup_ok_s);
        return 0;
    }
    GX8002_LOG(1u, 0x04800000u, fn_wakeup, 771u, wakeup_fail, wakeup_fail_s, status,
               response);
    return status;
}

int32_t SVC_SetMicGain(uint8_t gain)
{
    uint16_t response;
    int32_t status;

    audio_uart_buffer_zero(&response, 2u, 0u);
    status = GX8002_SetMicGain(gain, &response, GX8002_SVC_TIMEOUT);
    if (status == 0 && response == 1u) {
        GX8002_LOG(3u, 0x0c400000u, fn_gain, 802u, gain_ok, gain_ok_s, gain);
        return 0;
    }
    GX8002_LOG(1u, 0x04800000u, fn_gain, 799u, gain_fail, gain_fail_s, status, response);
    if (status == 0)
        status = -1;
    return status;
}

int32_t SVC_CodecMicDelay1Bit(void)
{
    uint8_t response;
    int32_t status;

    audio_uart_buffer_zero(&response, 1u, 0u);
    status = GX8002_MicDelay1Bit(&response, GX8002_SVC_TIMEOUT);
    if (status == 0 && response == 1u) {
        GX8002_LOG(3u, 0x0c000000u, fn_delay, 842u, delay_ok, delay_ok_s);
        return 0;
    }
    GX8002_LOG(1u, 0x04800000u, fn_delay, 839u, delay_fail, delay_fail_s, status,
               response);
    return status;
}
