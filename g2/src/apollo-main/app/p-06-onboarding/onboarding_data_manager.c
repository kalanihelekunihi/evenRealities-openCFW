/* Stock source: D:\01_workspace\s200_ap510b_iar_git\app\gui\onboarding\onboarding_data_manager.c
 * Native 0x47e2d0..0x47e60a (rows 0x47e2d0, 0x47e3e6, 0x47e470, 0x47e51c, 0x47e58e).
 * onboarding_notify_wear_status_to_app 0x47e320 and RPC_OnboardingFlagSendToPeer 0x47e4a6
 * are implemented elsewhere (onboarding_wear_notify_47e320.c, service_prepare5.c). */
#include <stdint.h>
#include "g2_kvdb.h"

/* Onboarding process record shared with the peer sync path (RAM 0x200f4800). */
typedef struct {
    uint8_t process_id; /* +0 */
    uint8_t substep;    /* +1 */
    uint8_t status;     /* +2: cleared on every handler call, 2 after a type-1 update */
} g2_onboarding_process_t;
_Static_assert(sizeof(g2_onboarding_process_t) == 3u, "stock byte record");

extern g2_onboarding_process_t g2_onboarding_process;  /* RAM 0x200f4800 */
extern void *g2_onboarding_mutex;                       /* RAM 0x20074830, osMutexId_t */
extern volatile uint32_t g2_onboarding_flag_dirty;      /* RAM 0x20074840 */
extern uint32_t g2_audio_log_event_handle;              /* RAM 0x20074570, osEventFlagsId_t */

extern int32_t osMutexAcquire(void *mutex, uint32_t timeout);
extern int32_t osMutexRelease(void *mutex);
extern uint32_t osEventFlagsSet(void *ef_id, uint32_t flags);
extern void audio_uart_buffer_zero(void *dst, uint32_t len, uint32_t fill); /* 0x43c0e4 */
extern uint32_t audio_uart_handshake_send(uint32_t channel, const void *bytes, uint32_t size,
                                          uint32_t flags, uint32_t timeout); /* 0x465480 */
extern uint32_t audio_log_flags(void);                                       /* 0x43d0ce */
extern void audio_log_extended(uint8_t level, const char *module, const char *path,
                               const char *function, uint32_t line, const char *format, ...); /* 0x43d574 */
extern uint32_t compress_log_output(uint32_t mask, const char *message,
                                    const char *message_copy, ...);          /* 0x43ce9e */

static const char module[] = "onboarding.data_mgr"; /* ROM 0x781570 */
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\onboarding\\onboarding_data_manager.c"; /* ROM 0x6e8ecc */
static const char save_function[] = "OnboardingFlagSaveToFlash";        /* ROM 0x76e964 */
static const char save_message[] = "OnboardingFlagSaveToFlash";         /* ROM 0x76e980 */
static const char save_short[] = "[onboarding.data_mgr]OnboardingFlagSaveToFlash"; /* ROM 0x7361c4 */
static const char save_failed[] = "OnboardingFlagSaveToFlash failed";   /* ROM 0x75732c */
static const char save_failed_short[] =
    "[onboarding.data_mgr]OnboardingFlagSaveToFlash failed";            /* ROM 0x720de0 */
static const char reply_function[] = "RPC_OnboardingFlagReplyToPeer";   /* ROM 0x762b90 */
static const char reply_message[] = "reply flag=%d to peer";            /* ROM 0x779d24 */
static const char reply_short[] = "[onboarding.data_mgr]reply flag=%d to peer"; /* ROM 0x740cb4 */
static const char sync_function[] = "RPC_OnboardingProcessSyncToPeer";  /* ROM 0x762bb0 */
static const char sync_message[] = "send process_id=%d, substep=%d to peer"; /* ROM 0x74bd74 */
static const char sync_short[] =
    "[onboarding.data_mgr]send process_id=%d, substep=%d to peer";      /* ROM 0x716f9c */

/* Peer RPC opcodes on handshake channel 0x10. */
#define ONBOARDING_RPC_PROCESS_SYNC 0x09u
#define ONBOARDING_RPC_FLAG_REPLY   0x0eu
#define ONBOARDING_RPC_CHANNEL      0x10u
#define ONBOARDING_RPC_TIMEOUT      5u

/* Types 2 and 3 are accepted without effect; 0 and >3 are rejected with 1.
 * A process-id change resets the substep before the new id is stored. */
uint32_t onboarding_common_data_handler(uint8_t type, const uint8_t *data)
{
    g2_onboarding_process.status = 0u;
    if (type == 1u) {
        (void)osMutexAcquire(g2_onboarding_mutex, 0xffffffffu);
        if (g2_onboarding_process.process_id != data[0])
            g2_onboarding_process.substep = 0u;
        g2_onboarding_process.process_id = data[0];
        g2_onboarding_process.status = 2u;
        (void)osMutexRelease(g2_onboarding_mutex);
    } else if (type == 0u || type > 3u) {
        return 1u;
    }
    return 0u;
}

/* Persists the onboarding flag when onboarding_flag_update marked it dirty. */
void OnboardingFlagSaveToFlash(void)
{
    if (g2_onboarding_flag_dirty != 1u)
        return;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, save_function, 0x5cu, save_message);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10000000u, save_short, save_short);
    if (SVC_KvdbBlobWriteOnboardingConfig() == 0) {
        g2_onboarding_flag_dirty = 0u;
        return;
    }
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(1u, module, path, save_function, 0x61u, save_failed);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x04000000u, save_failed_short, save_failed_short);
}

/* Stores a changed flag into the KVDB cache and wakes the log/persist
 * thread with event bit 4; the flash write happens later in
 * OnboardingFlagSaveToFlash. */
void onboarding_flag_update(uint32_t flag)
{
    uint32_t value = flag; /* stock passes the address of its spilled argument word */
    volatile uint8_t *current = kvdbOnboardingConfigPointer(0u);
    uint8_t stored = current != 0 ? *current : 0u;
    if (stored != (uint8_t)value) {
        (void)SVC_SetKvdbOnboardingConfig(0u, (const uint8_t *)&value);
        g2_onboarding_flag_dirty = 1u;
        (void)osEventFlagsSet((void *)(uintptr_t)g2_audio_log_event_handle, 4u);
    }
}

void RPC_OnboardingFlagReplyToPeer(uint8_t flag)
{
    uint8_t packet[2];
    audio_uart_buffer_zero(packet, sizeof packet, 0u);
    packet[0] = ONBOARDING_RPC_FLAG_REPLY;
    packet[1] = flag;
    (void)audio_uart_handshake_send(ONBOARDING_RPC_CHANNEL, packet, sizeof packet, 0u,
                                    ONBOARDING_RPC_TIMEOUT);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, reply_function, 0x8cu, reply_message,
                           (uint32_t)flag);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10400000u, reply_short, reply_short, (uint32_t)flag);
}

void RPC_OnboardingProcessSyncToPeer(void)
{
    uint8_t packet[3];
    audio_uart_buffer_zero(packet, sizeof packet, 0u);
    packet[0] = ONBOARDING_RPC_PROCESS_SYNC;
    packet[1] = g2_onboarding_process.process_id;
    packet[2] = g2_onboarding_process.substep;
    (void)audio_uart_handshake_send(ONBOARDING_RPC_CHANNEL, packet, sizeof packet, 0u,
                                    ONBOARDING_RPC_TIMEOUT);
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, sync_function, 0x9au, sync_message,
                           (uint32_t)g2_onboarding_process.process_id,
                           (uint32_t)g2_onboarding_process.substep);
    if ((audio_log_flags() & 1u) != 0u || (audio_log_flags() & 4u) != 0u)
        (void)compress_log_output(0x10800000u, sync_short, sync_short,
                                  (uint32_t)g2_onboarding_process.process_id,
                                  (uint32_t)g2_onboarding_process.substep);
}
