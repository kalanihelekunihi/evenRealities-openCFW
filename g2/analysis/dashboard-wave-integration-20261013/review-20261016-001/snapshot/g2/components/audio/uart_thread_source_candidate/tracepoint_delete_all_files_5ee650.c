/* Stock tracepoint_delete_all_files at 0x5ee650. */
#include <stdint.h>

extern void *audio_tracepoint_dir_open_474b02(const char *);
extern void *audio_tracepoint_dir_read_474bb8(void *);
extern int32_t audio_tracepoint_dir_close_474c66(void *);
extern void audio_tracepoint_storage_lock_47e088(void);
extern int32_t audio_tracepoint_parse_sequence_5edaf0(const char *, uint32_t *);
extern void audio_tracepoint_format_file_path_5edba2(char *, uint32_t, uint32_t);
extern int32_t audio_tracepoint_storage_unlink_47498c(const char *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char directory[] = "/log/tp";
static const char module[] = "tp.setting";
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\tracepoint\\tracepoint_setting.c";
static const char function_name[] = "tracepoint_delete_all_files";
static const char open_failed[] = "open tracepoint dir failed for delete all: %s";
static const char open_failed_short[] =
    "[tp.setting]open tracepoint dir failed for delete all: %s";
static const char removed[] = "tracepoint delete all removed: %s";
static const char removed_short[] = "[tp.setting]tracepoint delete all removed: %s";
static const char delete_failed[] = "tracepoint delete failed: %s";
static const char delete_failed_short[] = "[tp.setting]tracepoint delete failed: %s";

static void log_open_failed(void) {
    if (audio_log_flags() & 2u)
        audio_log_extended(1u, module, source_file, function_name, 0x17bu,
                           open_failed, directory);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x04400000u, open_failed_short,
                                    open_failed_short, directory);
}
static void log_removed(const char *path) {
    if (audio_log_flags() & 2u)
        audio_log_extended(4u, module, source_file, function_name, 0x18fu,
                           removed, path);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x10400000u, removed_short,
                                    removed_short, path);
}
static void log_delete_failed(const char *path) {
    if (audio_log_flags() & 2u)
        audio_log_extended(2u, module, source_file, function_name, 0x191u,
                           delete_failed, path);
    if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
        (void)compressed_log_output(0x08400000u, delete_failed_short,
                                    delete_failed_short, path);
}

int32_t audio_tracepoint_delete_all_files_5ee650(void) {
    void *directory_handle = audio_tracepoint_dir_open_474b02(directory);
    if (directory_handle == 0) {
        log_open_failed();
        return -1;
    }
    audio_tracepoint_storage_lock_47e088();
    uint32_t removed_count = 0u;
    for (;;) {
        const uint8_t *entry = (const uint8_t *)audio_tracepoint_dir_read_474bb8(
            directory_handle);
        if (entry == 0)
            break;
        if (entry[0x100u] != 8u)
            continue;
        uint32_t sequence = 0u;
        if (audio_tracepoint_parse_sequence_5edaf0((const char *)entry,
                                                   &sequence) == 0)
            continue;
        char path[80];
        audio_tracepoint_format_file_path_5edba2(path, 80u, sequence);
        if (audio_tracepoint_storage_unlink_47498c(path) == 0) {
            ++removed_count;
            log_removed(path);
        } else {
            log_delete_failed(path);
        }
    }
    (void)audio_tracepoint_dir_close_474c66(directory_handle);
    return (int32_t)removed_count;
}
