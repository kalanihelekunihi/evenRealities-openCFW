#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

static uint32_t test_mounted;
static char test_cwd[128];
static char test_printed[4096];
static size_t test_printed_length;
static uint8_t test_displayed[512];
static size_t test_displayed_length;
static char test_last_path[256];
static char test_last_path2[256];
static uint32_t test_last_mode;
static int32_t test_result;
static uint8_t test_file_data[256];
static size_t test_file_length;
static size_t test_file_cursor;
static unsigned test_dir_cursor;
static uint32_t test_block_size = 4096u;
static uint32_t test_block_count = 16u;
static int32_t test_used_blocks = 5;

#define OPEN_CFW_CLI_FS_MOUNTED test_mounted
#define OPEN_CFW_CLI_FS_VOLUME ((void *)(uintptr_t)0x1234u)
#define OPEN_CFW_CLI_FS_CWD test_cwd

static const char *test_parameter(const char *command, uint32_t index, uint32_t *length);
#define OPEN_CFW_CLI_FS_PARAMETER(c,i,n) test_parameter((c),(i),(n))
static void test_print(const char *format, ...);
#define OPEN_CFW_CLI_FS_PRINT(...) test_print(__VA_ARGS__)
static void test_display_byte(uint8_t value);
#define OPEN_CFW_CLI_FS_DISPLAY_BYTE(v) test_display_byte(v)
#define OPEN_CFW_CLI_FS_BLOCK_SIZE(v) ((void)(v), test_block_size)
#define OPEN_CFW_CLI_FS_BLOCK_COUNT(v) ((void)(v), test_block_count)

#include "../../components/apollo_main/core_overlay/freertos_cli_filesystem.c"

static const char *test_parameter(const char *command, uint32_t index, uint32_t *length)
{
    static char values[3][256];
    uint32_t current = 0u;
    const char *cursor = command;
    if (length != NULL) *length = 0u;
    if (command == NULL || index == 0u || index > 3u) return NULL;
    while (*cursor != '\0' && *cursor != ' ') ++cursor;
    while (*cursor != '\0') {
        size_t used = 0u;
        while (*cursor == ' ') ++cursor;
        if (*cursor == '\0') break;
        ++current;
        while (*cursor != '\0' && *cursor != ' ' && used + 1u < sizeof(values[0])) values[current - 1u][used++] = *cursor++;
        values[current - 1u][used] = '\0';
        if (current == index) {
            if (length != NULL) *length = (uint32_t)used;
            return values[current - 1u];
        }
    }
    return NULL;
}

static void test_print(const char *format, ...)
{
    va_list args;
    int written;
    if (test_printed_length >= sizeof(test_printed)) return;
    va_start(args, format);
    written = vsnprintf(test_printed + test_printed_length, sizeof(test_printed) - test_printed_length, format, args);
    va_end(args);
    if (written > 0) {
        size_t count = (size_t)written;
        if (count >= sizeof(test_printed) - test_printed_length) count = sizeof(test_printed) - test_printed_length - 1u;
        test_printed_length += count;
    }
}

static void test_display_byte(uint8_t value)
{
    if (test_displayed_length < sizeof(test_displayed)) test_displayed[test_displayed_length++] = value;
}

int32_t open_cfw_retained_cli_fs_stat(void *volume, const char *path, struct open_cfw_cli_fs_info *info)
{
    (void)volume;
    strncpy(test_last_path, path, sizeof(test_last_path) - 1u);
    test_last_path[sizeof(test_last_path) - 1u] = '\0';
    if (strcmp(path, "/work/sub") == 0 || strcmp(path, "/dest") == 0) {
        memset(info, 0, sizeof(*info)); info->type = 2u; strcpy(info->name, strcmp(path, "/dest") == 0 ? "dest" : "sub"); return 0;
    }
    if (strcmp(path, "/work/a") == 0) {
        memset(info, 0, sizeof(*info)); info->type = 1u; strcpy(info->name, "a"); info->size = (uint32_t)test_file_length; return 0;
    }
    return -2;
}

int32_t open_cfw_retained_cli_fs_file_open(void *volume, struct open_cfw_cli_fs_file *file, const char *path, uint32_t mode)
{
    (void)volume; (void)file; test_file_cursor = 0u; test_last_mode = mode;
    strncpy(test_last_path, path, sizeof(test_last_path) - 1u); test_last_path[sizeof(test_last_path) - 1u] = '\0';
    return test_result;
}

int32_t open_cfw_retained_cli_fs_file_read(void *volume, struct open_cfw_cli_fs_file *file, void *buffer, uint32_t size)
{
    size_t remaining; size_t count; (void)volume; (void)file;
    if (test_result < 0) return test_result;
    remaining = test_file_length - test_file_cursor;
    count = remaining < size ? remaining : size;
    memcpy(buffer, test_file_data + test_file_cursor, count); test_file_cursor += count;
    return (int32_t)count;
}

int32_t open_cfw_retained_cli_fs_file_close(void *volume, struct open_cfw_cli_fs_file *file) { (void)volume; (void)file; return 0; }
int32_t open_cfw_retained_cli_fs_remove(void *volume, const char *path) { (void)volume; strncpy(test_last_path,path,sizeof(test_last_path)-1u); return test_result; }
int32_t open_cfw_retained_cli_fs_rename(void *volume, const char *from, const char *to) { (void)volume; strncpy(test_last_path,from,sizeof(test_last_path)-1u); strncpy(test_last_path2,to,sizeof(test_last_path2)-1u); return test_result; }
int32_t open_cfw_retained_cli_fs_mkdir(void *volume, const char *path) { (void)volume; strncpy(test_last_path,path,sizeof(test_last_path)-1u); return test_result; }

int32_t open_cfw_retained_cli_fs_dir_open(void *volume, struct open_cfw_cli_fs_dir *dir, const char *path)
{
    (void)volume; (void)dir; test_dir_cursor = 0u; strncpy(test_last_path,path,sizeof(test_last_path)-1u);
    if (strcmp(path, "/work/sub") == 0 || strcmp(path, "/work") == 0) return test_result;
    return -2;
}

int32_t open_cfw_retained_cli_fs_dir_read(void *volume, struct open_cfw_cli_fs_dir *dir, struct open_cfw_cli_fs_info *info)
{
    static const char *names[] = {".", "..", "a", "sub"};
    (void)volume; (void)dir;
    if (test_dir_cursor >= 4u) return 0;
    memset(info,0,sizeof(*info)); strcpy(info->name,names[test_dir_cursor]); info->type = test_dir_cursor == 3u ? 2u : 1u; ++test_dir_cursor; return 1;
}

int32_t open_cfw_retained_cli_fs_dir_close(void *volume, struct open_cfw_cli_fs_dir *dir) { (void)volume; (void)dir; return 0; }
int32_t open_cfw_retained_cli_fs_size(void *volume) { (void)volume; return test_used_blocks; }

void open_cfw_retained_cli_fs_md5_init(struct open_cfw_cli_fs_md5 *context) { memset(context,0,sizeof(*context)); }
void open_cfw_retained_cli_fs_md5_update(struct open_cfw_cli_fs_md5 *context, const void *buffer, uint32_t size)
{
    const uint8_t *bytes = buffer; uint32_t i; for (i=0u;i<size;++i) context->opaque[i&31u] += bytes[i];
}
void open_cfw_retained_cli_fs_md5_final(uint8_t *digest, struct open_cfw_cli_fs_md5 *context)
{
    unsigned i; for (i=0u;i<16u;++i) digest[i]=(uint8_t)context->opaque[i];
}

void open_cfw_test_cli_fs_reset(void)
{
    test_mounted=1u; strcpy(test_cwd,"/work"); memset(test_printed,0,sizeof(test_printed)); test_printed_length=0u;
    memset(test_displayed,0,sizeof(test_displayed)); test_displayed_length=0u; memset(test_last_path,0,sizeof(test_last_path)); memset(test_last_path2,0,sizeof(test_last_path2));
    test_last_mode=0u; test_result=0; test_file_cursor=0u; test_file_length=3u; memcpy(test_file_data,"abc",3u); test_block_size=4096u; test_block_count=16u; test_used_blocks=5;
}
void open_cfw_test_cli_fs_set_mounted(uint32_t value) { test_mounted=value; }
void open_cfw_test_cli_fs_set_result(int32_t value) { test_result=value; }
const char *open_cfw_test_cli_fs_cwd(void) { return test_cwd; }
const char *open_cfw_test_cli_fs_printed(void) { return test_printed; }
const char *open_cfw_test_cli_fs_last_path(void) { return test_last_path; }
const char *open_cfw_test_cli_fs_last_path2(void) { return test_last_path2; }
uint32_t open_cfw_test_cli_fs_last_mode(void) { return test_last_mode; }
size_t open_cfw_test_cli_fs_displayed(uint8_t *output, size_t capacity) { size_t n=test_displayed_length<capacity?test_displayed_length:capacity; memcpy(output,test_displayed,n); return n; }
