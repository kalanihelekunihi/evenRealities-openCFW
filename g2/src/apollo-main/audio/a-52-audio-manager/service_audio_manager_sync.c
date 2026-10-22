/* Audio manager peer handshake, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\audio\service_audio_manager.c
 * (log tag "service.audio.manager"). Native 0x54f694..0x54f911; literal pool
 * 0x54f978..0x54fa1f (shared with the rest of the TU).
 * Not here: AUDM_activeAppCount 0x54f364 / AUDM_appAcquire 0x54f380
 * (app/even-ai/even_ai_app_acquire_54f380.c), AUDM_appRelease 0x54f50e
 * (app/even-ai/even_ai_app_release_54f50e.c), AUDM_common_data_handler 0x54f912
 * (system/registry-callback/registry_callback_54f912.c).
 *
 * The two arms exchange one status byte on common-data service 0x010c. Role 1
 * (master) owns the codec; role 2 (slave) only gates its DMIC:
 *   1 master -> slave  request: slave closes its DMIC and answers 2
 *   2 slave  -> master DMIC closed: master runs the codec check/upgrade,
 *                      answers 3 and marks itself initialised
 *   3 master -> slave  low-power done: slave reopens its DMIC
 *   4 slave  -> master slave ready: an uninitialised master answers 1
 * AUDM_Init on the slave upgrades/opens locally and sends 4; on the master it
 * drives codec GPIO line 6 high and sends 1. */
#include <stdint.h>

enum {
    AUDM_ROLE_MASTER = 1u,
    AUDM_ROLE_SLAVE = 2u,
};

enum {
    AUDM_SYNC_REQUEST_CLOSE_DMIC = 1u,
    AUDM_SYNC_DMIC_CLOSED = 2u,
    AUDM_SYNC_LOW_POWER_DONE = 3u,
    AUDM_SYNC_SLAVE_READY = 4u,
};

#define AUDM_SYNC_SERVICE 0x10cu

extern uint8_t g2_audio_app_acquired[8];         /* RAM 0x20074180 */
/* Set once the master has finished the codec check after the DMIC handshake. */
uint8_t g2_audm_master_initialized_2007500f;     /* RAM 0x2007500f */

extern uint8_t audio_uart_device_role_get(void);                                   /* 0x45a568 */
extern uint32_t audio_log_flags(void);                                             /* 0x43d0ce */
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);                       /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);    /* 0x43ce9e */
extern void *aeabi_memset_43c0e4(void *dst, uint32_t len, int32_t value);          /* 0x43c0e4 */
extern uint32_t audio_uart_request_send(uint32_t app, const void *bytes, uint32_t length,
                                        uint32_t id);                              /* 0x4651e0 */
extern int32_t audio_dsp_enable(void);                      /* SVC_CodecDMICOpen 0x57d6b4 */
extern int32_t audio_dsp_disable(void);                     /* SVC_CodecDMICClose 0x57d794 */
extern int32_t SVC_CodecCheckAndUpgrade(uint8_t force);     /* 0x579fb8 */
extern uint32_t g2_codec_gpio_write(uint32_t line, uint32_t value);                /* 0x509024 */

static const char module[] = "service.audio.manager"; /* ROM 0x77b38c */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\audio\\service_audio_manager.c"; /* ROM 0x6f5bfc */

static const char send_function[] = "AUDM_SendSyncMsgToPeer"; /* ROM 0x77b3d4 */
static const char send_msg[] = "sending audio sync msg to peer: msg_id=%d"; /* ROM 0x742b4c */
static const char send_short[] =
    "[service.audio.manager]sending audio sync msg to peer: msg_id=%d"; /* ROM 0x705518 */

static const char handle_function[] = "AUDM_HandlePeerSyncMsg"; /* ROM 0x77b3ec */
static const char slave_close[] = "slave: received request from master, closing DMIC"; /* ROM 0x72cea0 */
static const char slave_close_short[] =
    "[service.audio.manager]slave: received request from master, closing DMIC"; /* ROM 0x6f5c48 */
static const char master_closed[] =
    "master: received DMIC closed response, entering low power mode"; /* ROM 0x70e964 */
static const char master_closed_short[] =
    "[service.audio.manager]master: received DMIC closed response, entering low power mode"; /* ROM 0x6e4b10 */
static const char slave_reopen[] = "slave: received low power response, reopening DMIC"; /* ROM 0x72ced4 */
static const char slave_reopen_short[] =
    "[service.audio.manager]slave: received low power response, reopening DMIC"; /* ROM 0x6f5c94 */
static const char master_request[] = "master: not initialized, sending request to slave"; /* ROM 0x72cf08 */
static const char master_request_short[] =
    "[service.audio.manager]master: not initialized, sending request to slave"; /* ROM 0x6f5ce0 */
static const char unknown_msg[] = "unknown audio sync msg_id: %d"; /* ROM 0x7648b0 */
static const char unknown_short[] =
    "[service.audio.manager]unknown audio sync msg_id: %d"; /* ROM 0x722660 */

static const char init_function[] = "AUDM_Init"; /* ROM 0x78be58 */
static const char init_msg[] = "audio manager initialized, role=%d"; /* ROM 0x759240 */
static const char init_short[] =
    "[service.audio.manager]audio manager initialized, role=%d"; /* ROM 0x7182d4 */

static int compact_log_enabled(void)
{
    return (audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u;
}

void AUDM_SendSyncMsgToPeer(uint8_t msg_id)
{
    uint8_t payload = msg_id;

    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, send_function, 0x72u, send_msg, (uint32_t)msg_id);
    if (compact_log_enabled())
        (void)compress_log_output(0x0c400000u, send_short, send_short, (uint32_t)msg_id);
    (void)audio_uart_request_send(AUDM_SYNC_SERVICE, &payload, 1u, 0u);
}

void AUDM_HandlePeerSyncMsg(uint8_t msg_id)
{
    switch (msg_id) {
    case AUDM_SYNC_REQUEST_CLOSE_DMIC:
        if (audio_uart_device_role_get() != AUDM_ROLE_SLAVE)
            return;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, handle_function, 0x80u, slave_close);
        if (compact_log_enabled())
            (void)compress_log_output(0x0c000000u, slave_close_short, slave_close_short);
        (void)audio_dsp_disable();
        AUDM_SendSyncMsgToPeer(AUDM_SYNC_DMIC_CLOSED);
        return;
    case AUDM_SYNC_DMIC_CLOSED:
        if (audio_uart_device_role_get() != AUDM_ROLE_MASTER)
            return;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, handle_function, 0x88u, master_closed);
        if (compact_log_enabled())
            (void)compress_log_output(0x0c000000u, master_closed_short, master_closed_short);
        (void)SVC_CodecCheckAndUpgrade(0u);
        AUDM_SendSyncMsgToPeer(AUDM_SYNC_LOW_POWER_DONE);
        g2_audm_master_initialized_2007500f = 1u;
        return;
    case AUDM_SYNC_LOW_POWER_DONE:
        if (audio_uart_device_role_get() != AUDM_ROLE_SLAVE)
            return;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, handle_function, 0x91u, slave_reopen);
        if (compact_log_enabled())
            (void)compress_log_output(0x0c000000u, slave_reopen_short, slave_reopen_short);
        (void)audio_dsp_enable();
        return;
    case AUDM_SYNC_SLAVE_READY:
        if (audio_uart_device_role_get() != AUDM_ROLE_MASTER ||
            g2_audm_master_initialized_2007500f != 0u)
            return;
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(3u, module, path, handle_function, 0x9cu, master_request);
        if (compact_log_enabled())
            (void)compress_log_output(0x0c000000u, master_request_short, master_request_short);
        AUDM_SendSyncMsgToPeer(AUDM_SYNC_REQUEST_CLOSE_DMIC);
        return;
    default:
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(2u, module, path, handle_function, 0xa2u, unknown_msg,
                               (uint32_t)msg_id);
        if (compact_log_enabled())
            (void)compress_log_output(0x08400000u, unknown_short, unknown_short, (uint32_t)msg_id);
        return;
    }
}

int32_t AUDM_Init(void)
{
    uint8_t role;

    (void)aeabi_memset_43c0e4(g2_audio_app_acquired, sizeof g2_audio_app_acquired, 0);
    role = audio_uart_device_role_get();
    if (role == AUDM_ROLE_SLAVE) {
        (void)SVC_CodecCheckAndUpgrade(0u);
        (void)audio_dsp_enable();
        AUDM_SendSyncMsgToPeer(AUDM_SYNC_SLAVE_READY);
    } else {
        (void)g2_codec_gpio_write(6u, 1u);
        AUDM_SendSyncMsgToPeer(AUDM_SYNC_REQUEST_CLOSE_DMIC);
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(3u, module, path, init_function, 0xbdu, init_msg, (uint32_t)role);
    if (compact_log_enabled())
        (void)compress_log_output(0x0c400000u, init_short, init_short, (uint32_t)role);
    return 0;
}
