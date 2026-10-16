/* Stock text-stream completion and timer scheduling, 0x552f6a. */
#include <stdint.h>

extern char *strcpy(char *, const char *);
extern uint32_t audio_text_stream_buffer_create_553338(void *, void **, uint32_t *, uint32_t);
extern int32_t audio_file_mutex_acquire(void *, uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern void *audio_uart_timer_new(void (*)(void *), uint32_t, void *, const void *);
extern int32_t audio_timer_stop(void *);
extern int32_t audio_timer_start(void *, uint32_t);
extern int32_t audio_timer_delete(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern void audio_text_stream_tick_553054(void *);

static const char module[] = "text_stream_service";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\EvenAI\\text_stream_service.c";
static const char function[] = "animate_text";
static const char timer_error[] = "create animation timer failed";
static const char timer_error_short[] =
    "[text_stream_service]create animation timer failed";

static uint32_t word(const void *object, uint32_t offset) {
    return *(const uint32_t *)((const uint8_t *)object + offset);
}
static void callback(void *object) {
    uint32_t address = word(object, 0x18u);
    if (address)
        ((void (*)(void *))(uintptr_t)address)((void *)(uintptr_t)word(object, 0u));
}

void audio_text_stream_schedule_552f6a(void *object, uint32_t notify) {
    if (!object)
        return;
    ((uint8_t *)object)[0x14] = 0u;
    uint32_t copied = word(object, 0x0cu);
    uint32_t total = word(object, 0x10u);
    if ((int32_t)copied >= (int32_t)total) {
        if (!audio_text_stream_buffer_create_553338(
                object, (void **)object, (uint32_t *)((uint8_t *)object + 0x24u),
                total + 1u))
            return;
        strcpy((char *)(uintptr_t)word(object, 0u),
               (const char *)(uintptr_t)word(object, 4u));
        callback(object);
        return;
    }
    if (!(uint8_t)notify)
        return;
    void *mutex = (void *)(uintptr_t)word(object, 0x20u);
    if (!mutex || audio_file_mutex_acquire(mutex, UINT32_MAX) != 0)
        return;
    void *timer = (void *)(uintptr_t)word(object, 0x1cu);
    if (!timer) {
        timer = audio_uart_timer_new(audio_text_stream_tick_553054, 1u, object, 0);
        if (!timer) {
            if (audio_log_flags() & 2u)
                audio_log_extended(1u, module, path, function, 0x1d9u, timer_error);
            if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
                (void)compressed_log_output(0x04000000u, timer_error_short,
                                            timer_error_short);
            (void)audio_file_mutex_release(mutex);
            return;
        }
        *(uint32_t *)((uint8_t *)object + 0x1cu) = (uint32_t)(uintptr_t)timer;
    } else {
        (void)audio_timer_stop(timer);
    }
    if (audio_timer_start(timer, word(object, 8u)) != 0) {
        (void)audio_timer_delete(timer);
        *(uint32_t *)((uint8_t *)object + 0x1cu) = 0u;
    }
    (void)audio_file_mutex_release(mutex);
}
