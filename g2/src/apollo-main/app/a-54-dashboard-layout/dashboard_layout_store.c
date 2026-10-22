/* Dashboard layout accessors and /configure persistence helpers, stock
 * D:\01_workspace\s200_ap510b_iar_git\app\gui\dashboard\dashboard_layout.c
 * (log tag "dashboard.layout"). Native 0x558142..0x558147, 0x558314..0x558375,
 * 0x558632..0x558769 and 0x558804..0x5588a1; literal pool 0x5588a4..0x558948.
 *
 * The other functions of the same stock file live in
 * app/dashboard-layout/dashboard_layout_set.c (0x558030..0x558050, 0x558148,
 * 0x558376), app/pb-file/pb_file_exists.c (0x55876a) and
 * dashboard_watchface_cfg_equal.c (0x55819e, needs the FPU profile).
 *
 * The 128-byte layout: +0 base_pos, +1 widget_count (max 5), +2 widget_order[5],
 * +8 watchface config (kind byte first). */
#include <stdint.h>

extern uint8_t audio_dashboard_layout_current[128]; /* RAM 0x200e7934, literal 0x5588a8 */

extern int32_t dashboard_watchface_cfg_equal_55819e(const uint8_t *a, const uint8_t *b);

extern void *audio_tracepoint_dir_open_474b02(const char *path);  /* file_opendir */
extern int32_t audio_tracepoint_dir_close_474c66(void *dir);       /* file_closedir */
extern int32_t audio_tracepoint_storage_mkdir_474a76(const char *path, uint32_t mode); /* file_mkdir, 0 ok */
extern int32_t audio_tracepoint_storage_unlink_47498c(const char *path); /* file_remove, 0 ok */

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *, uint32_t, const char *, ...);
extern uint32_t compress_log_output(uint32_t, const char *, const char *, ...);

static const char module_tag[] = "dashboard.layout"; /* ROM 0x77ec1c */
static const char source_file[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_layout.c"; /* ROM 0x6f2cc8 */

static const char configure_dir[] = "/configure"; /* ROM 0x78a76c */
static const char fn_ensure_dir[] = "dashboard_layout_ensure_configure_dir"; /* ROM 0x748f5c */
static const char dir_exists[] = "configure dir exists: %s"; /* ROM 0x76aab8 */
static const char dir_exists_short[] = "[dashboard.layout]configure dir exists: %s"; /* ROM 0x73da00 */
static const char dir_created[] = "configure dir created: %s"; /* ROM 0x76aad4 */
static const char dir_created_short[] = "[dashboard.layout]configure dir created: %s"; /* ROM 0x73da2c */
static const char dir_race[] = "configure dir already exists (race): %s"; /* ROM 0x748f84 */
static const char dir_race_short[] = "[dashboard.layout]configure dir already exists (race): %s"; /* ROM 0x713edc */
static const char dir_failed[] = "create configure dir failed: %s"; /* ROM 0x75f1b0 */
static const char dir_failed_short[] = "[dashboard.layout]create configure dir failed: %s"; /* ROM 0x728720 */

static const char pb_path[] = "/configure/dashboard_ext.proto"; /* ROM 0x75f1f0 */
static const char fn_pb_delete[] = "dashboard_layout_pb_file_delete"; /* ROM 0x75f230 */
static const char pb_delete_failed[] = "layout pb file delete failed or not exist: %s (ret=%d)"; /* ROM 0x71da40 */
static const char pb_delete_failed_short[] =
    "[dashboard.layout]layout pb file delete failed or not exist: %s (ret=%d)"; /* ROM 0x6f2d60 */
static const char pb_deleted[] = "layout pb file deleted: %s"; /* ROM 0x76ab0c */
static const char pb_deleted_short[] = "[dashboard.layout]layout pb file deleted: %s"; /* ROM 0x732d74 */

static int log_extended_on(void) { return (audio_log_flags() & 2u) != 0u; }
static int log_compressed_on(void) { return (audio_log_flags() & 1u) || (audio_log_flags() & 4u); }

/* Stock 0x558142: the live layout copy. */
const uint8_t *dashboard_layout_get_current_558142(void)
{
    return audio_dashboard_layout_current;
}

/* Stock 0x558314: 1 when base_pos, widget_count, the used widget_order
 * entries and the watchface config all match; 0 otherwise or for NULL. */
int32_t dashboard_layout_equal_558314(const uint8_t *a, const uint8_t *b)
{
    if (a == 0 || b == 0)
        return 0;
    if (a[0] != b[0])
        return 0;
    if (a[1] != b[1])
        return 0;
    for (uint8_t i = 0u; i < a[1]; i++) {
        if (a[2u + i] != b[2u + i])
            return 0;
    }
    if (dashboard_watchface_cfg_equal_55819e(a + 8, b + 8) == 0)
        return 0;
    return 1;
}

/* Stock 0x558632: make sure "/configure" exists; 0 ok, -1 when it can be
 * neither opened nor created. */
int32_t dashboard_layout_ensure_configure_dir_558632(void)
{
    const char *dir = configure_dir;
    void *handle = audio_tracepoint_dir_open_474b02(dir);

    if (handle != 0) {
        (void)audio_tracepoint_dir_close_474c66(handle);
        if (log_extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_ensure_dir, 0x11fu, dir_exists, dir);
        if (log_compressed_on())
            (void)compress_log_output(0x10400000u, dir_exists_short, dir_exists_short, dir);
        return 0;
    }
    if (audio_tracepoint_storage_mkdir_474a76(dir, 0u) == 0) {
        if (log_extended_on())
            audio_log_extended(3u, module_tag, source_file, fn_ensure_dir, 0x128u, dir_created, dir);
        if (log_compressed_on())
            (void)compress_log_output(0x0c400000u, dir_created_short, dir_created_short, dir);
        return 0;
    }
    handle = audio_tracepoint_dir_open_474b02(dir);
    if (handle != 0) {
        (void)audio_tracepoint_dir_close_474c66(handle);
        if (log_extended_on())
            audio_log_extended(4u, module_tag, source_file, fn_ensure_dir, 0x130u, dir_race, dir);
        if (log_compressed_on())
            (void)compress_log_output(0x10400000u, dir_race_short, dir_race_short, dir);
        return 0;
    }
    if (log_extended_on())
        audio_log_extended(1u, module_tag, source_file, fn_ensure_dir, 0x134u, dir_failed, dir);
    if (log_compressed_on())
        (void)compress_log_output(0x04400000u, dir_failed_short, dir_failed_short, dir);
    return -1;
}

/* Stock 0x558804: remove /configure/dashboard_ext.proto; 0 ok, -1 on error. */
int32_t dashboard_layout_pb_file_delete_558804(void)
{
    const char *path = pb_path;
    int32_t ret = audio_tracepoint_storage_unlink_47498c(path);

    if (ret != 0) {
        if (log_extended_on())
            audio_log_extended(2u, module_tag, source_file, fn_pb_delete, 0x14cu, pb_delete_failed, path, ret);
        if (log_compressed_on())
            (void)compress_log_output(0x08800000u, pb_delete_failed_short, pb_delete_failed_short, path, ret);
        return -1;
    }
    if (log_extended_on())
        audio_log_extended(3u, module_tag, source_file, fn_pb_delete, 0x14fu, pb_deleted, path);
    if (log_compressed_on())
        (void)compress_log_output(0x0c400000u, pb_deleted_short, pb_deleted_short, path);
    return 0;
}
