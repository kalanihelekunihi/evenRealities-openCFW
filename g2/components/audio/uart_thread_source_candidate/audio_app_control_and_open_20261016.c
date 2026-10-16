/* Stock audio packet queue facade 0x53c638 and hardware-open wrapper 0x591374. */
#include <stdint.h>

extern int32_t audio_cmsis_queue_put(void *, const void *, uint32_t, uint32_t);
extern uint32_t audio_thread_flags_set(void *, uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern void *audio_app_hardware_core_59123a(uint32_t, uint32_t, uint32_t,
                                             uint32_t, void *);

/* Stock audio thread context starts at 0x20003f98; accessed through +0x0f. */
uint8_t g2_audio_control_context_20003f98[0x10];
static const char module[] = "thread.audio";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\platform\\threads\\thread_audio.c";
static const char function[] = "AUD_SendMessage";
static const char failed[] = "osMessageQueuePut error:0x%x";
static const char failed_short[] =
    "[thread.audio]osMessageQueuePut error:0x%x";

void audio_app_control_packet_53c638(const void *packet) {
    if (!packet)
        return;
    uint32_t queue = *(uint32_t *)(g2_audio_control_context_20003f98 + 0x0cu);
    if (!queue)
        return;
    int32_t result = audio_cmsis_queue_put((void *)(uintptr_t)queue, packet, 0u, 0u);
    if (result == 0) {
        uint32_t thread = *(uint32_t *)(g2_audio_control_context_20003f98 + 8u);
        (void)audio_thread_flags_set((void *)(uintptr_t)thread, 0x00400000u);
        return;
    }
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, path, function, 0x119u, failed,
                           (uint32_t)result);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x04400000u, failed_short,
                                    failed_short, (uint32_t)result);
}

void *audio_app_hardware_open_591374(uint32_t first, uint32_t second,
                                      uint32_t third, void *fourth) {
    return audio_app_hardware_core_59123a(0u, first, second, third, fourth);
}
