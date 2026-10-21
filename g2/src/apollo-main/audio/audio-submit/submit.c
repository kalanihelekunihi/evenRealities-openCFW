#include <stdint.h>

/* AUD_SendMessage, native 0x53c638..0x53c6b1. Product dispatch
 * state at 0x20003f98 owns queue at +12 and task at +8. */
extern uint8_t g2_audio_dispatch_state[];
extern int32_t audio_cmsis_queue_put(void *queue, const void *message,
                                     uint8_t priority, uint32_t timeout);
extern uint32_t audio_flags_set(void *task, uint32_t flags);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint32_t level, const char *module,
                               const char *file, const char *function,
                               uint32_t line, const char *format, ...);
extern void audio_log_simple(uint32_t mask, const char *format,
                             const char *copy, ...);

static const char module[] = "thread.audio";
static const char file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_audio.c";
static const char function[] = "AUD_SendMessage";
static const char failed[] = "osMessageQueuePut error:0x%x";
static const char simple_failed[] =
    "[thread.audio]osMessageQueuePut error:0x%x";

void stock_audio_submit(const void *message) {
    if (message == 0)
        return;
    void *const queue = *(void **)(g2_audio_dispatch_state + 12u);
    if (queue == 0)
        return;
    const int32_t status = audio_cmsis_queue_put(queue, message, 0u, 0u);
    if (status == 0) {
        void *const task = *(void **)(g2_audio_dispatch_state + 8u);
        (void)audio_flags_set(task, 0x400000u);
        return;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, file, function, 281u,
                           failed, status);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        audio_log_simple(0x04400000u, simple_failed,
                         simple_failed, status);
}
