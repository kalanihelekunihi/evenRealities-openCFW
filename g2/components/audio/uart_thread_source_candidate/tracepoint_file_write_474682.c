/* Stock redirect _fwrite at 0x474682, used by the tracepoint writer. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern int32_t audio_file_mutex_acquire(void *, uint32_t);
extern int32_t audio_file_mutex_release(void *);
extern int32_t audio_file_lfs_write_4cfb7c(void *, void *, const void *, uint32_t);
extern void *audio_file_api_mutex;

static const char module[] = "redirect";
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\product\\s200\\app\\config\\redirect.c";
static const char function_name[] = "_fwrite";
static const char null_text[] = "fwrite: stream is NULL";
static const char null_short[] = "[redirect]fwrite: stream is NULL";
static const char timeout_text[] = "fwrite: mutex timeout, want=%u bytes";
static const char timeout_short[] = "[redirect]fwrite: mutex timeout, want=%u bytes";
static const char error_text[] = "fwrite: lfs_file_write err=%d, want=%u bytes";
static const char error_short[] = "[redirect]fwrite: lfs_file_write err=%d, want=%u bytes";
static const char short_text[] = "fwrite: short write, got=%d, want=%u";
static const char short_short[] = "[redirect]fwrite: short write, got=%d, want=%u";

static void log_null(void) {
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, source_file, function_name, 0x236u,
                           null_text);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x04000000u, null_short, null_short);
}
static void log_timeout(uint32_t bytes) {
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, source_file, function_name, 0x23cu,
                           timeout_text, bytes);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x04400000u, timeout_short,
                                    timeout_short, bytes);
}
static void log_error(int32_t result, uint32_t bytes) {
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, source_file, function_name, 0x24au,
                           error_text, result, bytes);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x04800000u, error_short, error_short,
                                    result, bytes);
}
static void log_short(int32_t result, uint32_t bytes) {
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module, source_file, function_name, 0x24eu,
                           short_text, result, bytes);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x08800000u, short_short, short_short,
                                    result, bytes);
}

uint32_t audio_tracepoint_file_write_474682(const void *buffer, uint32_t size,
                                             uint32_t count, void *stream) {
    uint32_t bytes = size * count;
    if (stream == 0) {
        log_null();
        return 0u;
    }
    if (audio_file_mutex_acquire(audio_file_api_mutex, 1000u) != 0) {
        log_timeout(bytes);
        return 0u;
    }
    void *filesystem = (void *)(uintptr_t)*(uint32_t *)stream;
    int32_t written = audio_file_lfs_write_4cfb7c(filesystem,
                                                    (uint8_t *)stream + 4u,
                                                    buffer, bytes);
    (void)audio_file_mutex_release(audio_file_api_mutex);
    if (written < 0) {
        log_error(written, bytes);
        return 0u;
    }
    if ((uint32_t)written < bytes)
        log_short(written, bytes);
    uint32_t items;
    __asm volatile("udiv %0, %1, %2" : "=r"(items)
                   : "r"((uint32_t)written), "r"(size));
    return items;
}
