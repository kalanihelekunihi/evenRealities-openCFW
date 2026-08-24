/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room implementation of the twelve linked entries in G2's
 * kernel/FreeRTOS-Plus-CLI/prvCommand/prvCommand_filesystem.c object.
 * The command policy is independent first-party code; filesystem operations
 * remain behind the authenticated littlefs adapter seam.
 */

#include <stddef.h>
#include <stdint.h>

#define OPEN_CFW_CLI_FS_PATH_MAX 256u
#define OPEN_CFW_CLI_FS_READ_CHUNK 64u
#define OPEN_CFW_CLI_FS_TYPE_DIRECTORY 2u
#define OPEN_CFW_CLI_FS_O_RDONLY 1u
#define OPEN_CFW_CLI_FS_O_WRONLY 2u
#define OPEN_CFW_CLI_FS_O_CREAT 0x100u

struct open_cfw_cli_fs_info {
    uint8_t type;
    uint32_t size;
    char name[256];
};

struct open_cfw_cli_fs_file {
    uintptr_t opaque[40];
};

struct open_cfw_cli_fs_dir {
    uintptr_t opaque[40];
};

struct open_cfw_cli_fs_md5 {
    uint32_t opaque[32];
};

struct open_cfw_cli_fs_block_stats {
    uint32_t free_bytes;
    uint32_t used_bytes;
    uint32_t blocks;
    uint32_t used_blocks;
};

#ifndef OPEN_CFW_CLI_FS_MOUNTED
#define OPEN_CFW_CLI_FS_MOUNTED (*(volatile uint32_t *)(uintptr_t)0x200746a8u)
#endif
#ifndef OPEN_CFW_CLI_FS_VOLUME
#define OPEN_CFW_CLI_FS_VOLUME ((void *)(uintptr_t)0x20071ac8u)
#endif
#ifndef OPEN_CFW_CLI_FS_CWD
#define OPEN_CFW_CLI_FS_CWD ((char *)(uintptr_t)0x200031b4u)
#endif

#ifndef OPEN_CFW_CLI_FS_PARAMETER
const char *open_cfw_retained_cli_fs_parameter(const char *, uint32_t, uint32_t *);
#define OPEN_CFW_CLI_FS_PARAMETER(c,i,n) open_cfw_retained_cli_fs_parameter((c),(i),(n))
#endif
#ifndef OPEN_CFW_CLI_FS_PRINT
void open_cfw_retained_cli_fs_print(const char *, ...);
#define OPEN_CFW_CLI_FS_PRINT(...) open_cfw_retained_cli_fs_print(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_CLI_FS_DISPLAY_BYTE
void open_cfw_retained_cli_fs_display_byte(uint8_t);
#define OPEN_CFW_CLI_FS_DISPLAY_BYTE(v) open_cfw_retained_cli_fs_display_byte(v)
#endif
#ifndef OPEN_CFW_CLI_FS_STAT
int32_t open_cfw_retained_cli_fs_stat(void *, const char *, struct open_cfw_cli_fs_info *);
#define OPEN_CFW_CLI_FS_STAT(v,p,i) open_cfw_retained_cli_fs_stat((v),(p),(i))
#endif
#ifndef OPEN_CFW_CLI_FS_FILE_OPEN
int32_t open_cfw_retained_cli_fs_file_open(void *, struct open_cfw_cli_fs_file *, const char *, uint32_t);
#define OPEN_CFW_CLI_FS_FILE_OPEN(v,f,p,m) open_cfw_retained_cli_fs_file_open((v),(f),(p),(m))
#endif
#ifndef OPEN_CFW_CLI_FS_FILE_READ
int32_t open_cfw_retained_cli_fs_file_read(void *, struct open_cfw_cli_fs_file *, void *, uint32_t);
#define OPEN_CFW_CLI_FS_FILE_READ(v,f,b,n) open_cfw_retained_cli_fs_file_read((v),(f),(b),(n))
#endif
#ifndef OPEN_CFW_CLI_FS_FILE_CLOSE
int32_t open_cfw_retained_cli_fs_file_close(void *, struct open_cfw_cli_fs_file *);
#define OPEN_CFW_CLI_FS_FILE_CLOSE(v,f) open_cfw_retained_cli_fs_file_close((v),(f))
#endif
#ifndef OPEN_CFW_CLI_FS_REMOVE
int32_t open_cfw_retained_cli_fs_remove(void *, const char *);
#define OPEN_CFW_CLI_FS_REMOVE(v,p) open_cfw_retained_cli_fs_remove((v),(p))
#endif
#ifndef OPEN_CFW_CLI_FS_RENAME
int32_t open_cfw_retained_cli_fs_rename(void *, const char *, const char *);
#define OPEN_CFW_CLI_FS_RENAME(v,a,b) open_cfw_retained_cli_fs_rename((v),(a),(b))
#endif
#ifndef OPEN_CFW_CLI_FS_MKDIR
int32_t open_cfw_retained_cli_fs_mkdir(void *, const char *);
#define OPEN_CFW_CLI_FS_MKDIR(v,p) open_cfw_retained_cli_fs_mkdir((v),(p))
#endif
#ifndef OPEN_CFW_CLI_FS_DIR_OPEN
int32_t open_cfw_retained_cli_fs_dir_open(void *, struct open_cfw_cli_fs_dir *, const char *);
#define OPEN_CFW_CLI_FS_DIR_OPEN(v,d,p) open_cfw_retained_cli_fs_dir_open((v),(d),(p))
#endif
#ifndef OPEN_CFW_CLI_FS_DIR_READ
int32_t open_cfw_retained_cli_fs_dir_read(void *, struct open_cfw_cli_fs_dir *, struct open_cfw_cli_fs_info *);
#define OPEN_CFW_CLI_FS_DIR_READ(v,d,i) open_cfw_retained_cli_fs_dir_read((v),(d),(i))
#endif
#ifndef OPEN_CFW_CLI_FS_DIR_CLOSE
int32_t open_cfw_retained_cli_fs_dir_close(void *, struct open_cfw_cli_fs_dir *);
#define OPEN_CFW_CLI_FS_DIR_CLOSE(v,d) open_cfw_retained_cli_fs_dir_close((v),(d))
#endif
#ifndef OPEN_CFW_CLI_FS_SIZE
int32_t open_cfw_retained_cli_fs_size(void *);
#define OPEN_CFW_CLI_FS_SIZE(v) open_cfw_retained_cli_fs_size(v)
#endif
#ifndef OPEN_CFW_CLI_FS_BLOCK_SIZE
#define OPEN_CFW_CLI_FS_CONFIG(v) \
    (*(const uintptr_t *)((const uint8_t *)(v) + 0x68u))
#define OPEN_CFW_CLI_FS_BLOCK_SIZE(v) \
    (*(const uint32_t *)(OPEN_CFW_CLI_FS_CONFIG(v) + 0x1cu))
#endif
#ifndef OPEN_CFW_CLI_FS_BLOCK_COUNT
#define OPEN_CFW_CLI_FS_BLOCK_COUNT(v) \
    (*(const uint32_t *)(OPEN_CFW_CLI_FS_CONFIG(v) + 0x20u))
#endif
#ifndef OPEN_CFW_CLI_FS_MD5_INIT
void open_cfw_retained_cli_fs_md5_init(struct open_cfw_cli_fs_md5 *);
#define OPEN_CFW_CLI_FS_MD5_INIT(c) open_cfw_retained_cli_fs_md5_init(c)
#endif
#ifndef OPEN_CFW_CLI_FS_MD5_UPDATE
void open_cfw_retained_cli_fs_md5_update(struct open_cfw_cli_fs_md5 *, const void *, uint32_t);
#define OPEN_CFW_CLI_FS_MD5_UPDATE(c,b,n) open_cfw_retained_cli_fs_md5_update((c),(b),(n))
#endif
#ifndef OPEN_CFW_CLI_FS_MD5_FINAL
void open_cfw_retained_cli_fs_md5_final(uint8_t *, struct open_cfw_cli_fs_md5 *);
#define OPEN_CFW_CLI_FS_MD5_FINAL(o,c) open_cfw_retained_cli_fs_md5_final((o),(c))
#endif

static __attribute__((unused, always_inline)) inline int32_t open_cfw_cli_fs_streq(const char *left, const char *right)
{
    size_t index = 0u;
    if (left == NULL || right == NULL) return 0;
    while (left[index] == right[index]) {
        if (left[index] == '\0') return 1;
        ++index;
    }
    return 0;
}

static __attribute__((unused, always_inline)) inline int32_t open_cfw_cli_fs_copy(char *output, size_t capacity, const char *input)
{
    size_t index = 0u;
    if (output == NULL || capacity == 0u || input == NULL) return -1;
    while (input[index] != '\0') {
        if (index + 1u >= capacity) { output[0] = '\0'; return -1; }
        output[index] = input[index];
        ++index;
    }
    output[index] = '\0';
    return 0;
}

static __attribute__((unused, always_inline)) inline int32_t open_cfw_cli_fs_join(char *output, size_t capacity, const char *base, const char *name)
{
    size_t used = 0u;
    size_t index = 0u;
    if (output == NULL || capacity == 0u || base == NULL || name == NULL) return -1;
    if (name[0] == '/') return open_cfw_cli_fs_copy(output, capacity, name);
    while (base[used] != '\0') {
        if (used + 1u >= capacity) return -1;
        output[used] = base[used];
        ++used;
    }
    if (used == 0u || output[used - 1u] != '/') {
        if (used + 1u >= capacity) return -1;
        output[used++] = '/';
    }
    while (name[index] != '\0') {
        if (used + 1u >= capacity) return -1;
        output[used++] = name[index++];
    }
    output[used] = '\0';
    return 0;
}

static __attribute__((unused, always_inline)) inline const char *open_cfw_cli_fs_arg(const char *command, uint32_t index, uint32_t *length)
{
    const char *value = OPEN_CFW_CLI_FS_PARAMETER(command, index, length);
    if (value == NULL || length == NULL || *length == 0u) return NULL;
    return value;
}

int32_t open_cfw_cli_fs_ls(char *, uint32_t, const char *);
int32_t open_cfw_cli_fs_cat(char *, uint32_t, const char *);
int32_t open_cfw_cli_fs_rm(char *, uint32_t, const char *);
int32_t open_cfw_cli_fs_normalize_path(char *, const char *);
int32_t open_cfw_cli_fs_cd(char *, uint32_t, const char *);
int32_t open_cfw_cli_fs_mkdir(char *, uint32_t, const char *);
int32_t open_cfw_cli_fs_touch(char *, uint32_t, const char *);
int32_t open_cfw_cli_fs_pwd(char *, uint32_t, const char *);
int32_t open_cfw_cli_fs_mv(char *, uint32_t, const char *);
int32_t open_cfw_cli_fs_md5(char *, uint32_t, const char *);
int32_t open_cfw_cli_fs_df(char *, uint32_t, const char *);
void open_cfw_cli_fs_block_stats_accumulate(uint32_t, uint32_t, uint32_t, struct open_cfw_cli_fs_block_stats *);

#if !defined(OPEN_CFW_CLI_FS_LS_ONLY) && !defined(OPEN_CFW_CLI_FS_CAT_ONLY) && !defined(OPEN_CFW_CLI_FS_RM_ONLY) && !defined(OPEN_CFW_CLI_FS_NORMALIZE_ONLY) && !defined(OPEN_CFW_CLI_FS_CD_ONLY) && !defined(OPEN_CFW_CLI_FS_MKDIR_ONLY) && !defined(OPEN_CFW_CLI_FS_TOUCH_ONLY) && !defined(OPEN_CFW_CLI_FS_PWD_ONLY) && !defined(OPEN_CFW_CLI_FS_MV_ONLY) && !defined(OPEN_CFW_CLI_FS_MD5_ONLY) && !defined(OPEN_CFW_CLI_FS_DF_ONLY) && !defined(OPEN_CFW_CLI_FS_BLOCK_STATS_ONLY)
#define OPEN_CFW_CLI_FS_BUILD_ALL 1
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_NORMALIZE_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_cli_fs_normalize_path(char *output, const char *input)
{
    size_t marks[OPEN_CFW_CLI_FS_PATH_MAX / 2u];
    size_t depth = 0u;
    size_t source = 0u;
    size_t used = 1u;
    if (output == NULL || input == NULL) return -1;
    output[0] = '/';
    output[1] = '\0';
    while (input[source] != '\0') {
        size_t begin;
        size_t length;
        while (input[source] == '/') ++source;
        begin = source;
        while (input[source] != '\0' && input[source] != '/') ++source;
        length = source - begin;
        if (length == 0u || (length == 1u && input[begin] == '.')) continue;
        if (length == 2u && input[begin] == '.' && input[begin + 1u] == '.') {
            if (depth != 0u) {
                used = marks[--depth];
                output[used] = '\0';
            }
            continue;
        }
        if (used != 1u) {
            if (used + 1u >= OPEN_CFW_CLI_FS_PATH_MAX) return -1;
            output[used++] = '/';
        }
        if (depth >= sizeof(marks) / sizeof(marks[0])) return -1;
        marks[depth++] = used == 1u ? 1u : used - 1u;
        if (used + length >= OPEN_CFW_CLI_FS_PATH_MAX) return -1;
        while (length-- != 0u) output[used++] = input[begin++];
        output[used] = '\0';
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_LS_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_cli_fs_ls(char *output, uint32_t output_length, const char *command)
{
    struct open_cfw_cli_fs_dir dir;
    struct open_cfw_cli_fs_info info;
    int32_t result;
    (void)output; (void)output_length; (void)command;
    if (OPEN_CFW_CLI_FS_MOUNTED != 1u) return 0;
    result = OPEN_CFW_CLI_FS_DIR_OPEN(OPEN_CFW_CLI_FS_VOLUME, &dir, OPEN_CFW_CLI_FS_CWD);
    if (result < 0) return 0;
    while ((result = OPEN_CFW_CLI_FS_DIR_READ(OPEN_CFW_CLI_FS_VOLUME, &dir, &info)) > 0) {
        if (open_cfw_cli_fs_streq(info.name, ".") || open_cfw_cli_fs_streq(info.name, "..")) continue;
        OPEN_CFW_CLI_FS_PRINT("%s%s\r\n", info.name, info.type == OPEN_CFW_CLI_FS_TYPE_DIRECTORY ? "/" : "");
    }
    (void)OPEN_CFW_CLI_FS_DIR_CLOSE(OPEN_CFW_CLI_FS_VOLUME, &dir);
    return 0;
}
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_CAT_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_cli_fs_cat(char *output, uint32_t output_length, const char *command)
{
    struct open_cfw_cli_fs_file file;
    uint8_t buffer[OPEN_CFW_CLI_FS_READ_CHUNK];
    char path[OPEN_CFW_CLI_FS_PATH_MAX];
    uint32_t length = 0u;
    const char *name;
    int32_t count;
    uint32_t index;
    (void)output; (void)output_length;
    if (OPEN_CFW_CLI_FS_MOUNTED != 1u) return 0;
    name = open_cfw_cli_fs_arg(command, 1u, &length);
    if (name == NULL || open_cfw_cli_fs_join(path, sizeof(path), OPEN_CFW_CLI_FS_CWD, name) != 0) {
        OPEN_CFW_CLI_FS_PRINT("error path name\r\n");
        return 0;
    }
    if (OPEN_CFW_CLI_FS_FILE_OPEN(OPEN_CFW_CLI_FS_VOLUME, &file, path, OPEN_CFW_CLI_FS_O_RDONLY) != 0) return 0;
    while ((count = OPEN_CFW_CLI_FS_FILE_READ(OPEN_CFW_CLI_FS_VOLUME, &file, buffer, sizeof(buffer))) > 0) {
        for (index = 0u; index < (uint32_t)count; ++index) OPEN_CFW_CLI_FS_DISPLAY_BYTE(buffer[index]);
    }
    (void)OPEN_CFW_CLI_FS_FILE_CLOSE(OPEN_CFW_CLI_FS_VOLUME, &file);
    return 0;
}
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_RM_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_cli_fs_rm(char *output, uint32_t output_length, const char *command)
{
    char path[OPEN_CFW_CLI_FS_PATH_MAX];
    uint32_t length = 0u;
    const char *name;
    (void)output; (void)output_length;
    if (OPEN_CFW_CLI_FS_MOUNTED != 1u) return 0;
    name = open_cfw_cli_fs_arg(command, 1u, &length);
    if (name == NULL || open_cfw_cli_fs_join(path, sizeof(path), OPEN_CFW_CLI_FS_CWD, name) != 0) {
        OPEN_CFW_CLI_FS_PRINT("error path name\r\n");
        return 0;
    }
    (void)OPEN_CFW_CLI_FS_REMOVE(OPEN_CFW_CLI_FS_VOLUME, path);
    return 0;
}
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_CD_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_cli_fs_cd(char *output, uint32_t output_length, const char *command)
{
    struct open_cfw_cli_fs_dir dir;
    char joined[OPEN_CFW_CLI_FS_PATH_MAX];
    char normalized[OPEN_CFW_CLI_FS_PATH_MAX];
    uint32_t length = 0u;
    const char *name;
    (void)output; (void)output_length;
    if (OPEN_CFW_CLI_FS_MOUNTED != 1u) return 0;
    name = open_cfw_cli_fs_arg(command, 1u, &length);
    if (name == NULL || open_cfw_cli_fs_join(joined, sizeof(joined), OPEN_CFW_CLI_FS_CWD, name) != 0 || open_cfw_cli_fs_normalize_path(normalized, joined) != 0) {
        OPEN_CFW_CLI_FS_PRINT("invaild path !\r\n");
        return 0;
    }
    if (OPEN_CFW_CLI_FS_DIR_OPEN(OPEN_CFW_CLI_FS_VOLUME, &dir, normalized) != 0) {
        OPEN_CFW_CLI_FS_PRINT("invaild path !\r\n");
        return 0;
    }
    (void)OPEN_CFW_CLI_FS_DIR_CLOSE(OPEN_CFW_CLI_FS_VOLUME, &dir);
    (void)open_cfw_cli_fs_copy(OPEN_CFW_CLI_FS_CWD, 128u, normalized);
    return 0;
}
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_MKDIR_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_cli_fs_mkdir(char *output, uint32_t output_length, const char *command)
{
    char path[OPEN_CFW_CLI_FS_PATH_MAX];
    uint32_t length = 0u;
    const char *name;
    (void)output; (void)output_length;
    if (OPEN_CFW_CLI_FS_MOUNTED != 1u) return 0;
    name = open_cfw_cli_fs_arg(command, 1u, &length);
    if (name == NULL || open_cfw_cli_fs_join(path, sizeof(path), OPEN_CFW_CLI_FS_CWD, name) != 0) {
        OPEN_CFW_CLI_FS_PRINT("error path name\r\n");
        return 0;
    }
    if (OPEN_CFW_CLI_FS_MKDIR(OPEN_CFW_CLI_FS_VOLUME, path) != 0) OPEN_CFW_CLI_FS_PRINT("Directory creation failed\r\n");
    return 0;
}
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_TOUCH_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_cli_fs_touch(char *output, uint32_t output_length, const char *command)
{
    struct open_cfw_cli_fs_file file;
    char path[OPEN_CFW_CLI_FS_PATH_MAX];
    uint32_t length = 0u;
    const char *name;
    (void)output; (void)output_length;
    if (OPEN_CFW_CLI_FS_MOUNTED != 1u) return 0;
    name = open_cfw_cli_fs_arg(command, 1u, &length);
    if (name == NULL || open_cfw_cli_fs_join(path, sizeof(path), OPEN_CFW_CLI_FS_CWD, name) != 0) {
        OPEN_CFW_CLI_FS_PRINT("error path name\r\n");
        return 0;
    }
    if (OPEN_CFW_CLI_FS_FILE_OPEN(OPEN_CFW_CLI_FS_VOLUME, &file, path, OPEN_CFW_CLI_FS_O_WRONLY | OPEN_CFW_CLI_FS_O_CREAT) != 0) {
        OPEN_CFW_CLI_FS_PRINT("File creation failed\r\n");
    } else {
        (void)OPEN_CFW_CLI_FS_FILE_CLOSE(OPEN_CFW_CLI_FS_VOLUME, &file);
    }
    return 0;
}
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_PWD_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_cli_fs_pwd(char *output, uint32_t output_length, const char *command)
{
    (void)output; (void)output_length; (void)command;
    if (OPEN_CFW_CLI_FS_MOUNTED == 1u) OPEN_CFW_CLI_FS_PRINT("%s\r\n", OPEN_CFW_CLI_FS_CWD);
    return 0;
}
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_MV_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_cli_fs_mv(char *output, uint32_t output_length, const char *command)
{
    struct open_cfw_cli_fs_info source_info;
    struct open_cfw_cli_fs_info destination_info;
    char source_joined[OPEN_CFW_CLI_FS_PATH_MAX];
    char destination_joined[OPEN_CFW_CLI_FS_PATH_MAX];
    char source[OPEN_CFW_CLI_FS_PATH_MAX];
    char destination[OPEN_CFW_CLI_FS_PATH_MAX];
    char final_destination[OPEN_CFW_CLI_FS_PATH_MAX];
    uint32_t source_length = 0u;
    uint32_t destination_length = 0u;
    const char *source_arg;
    const char *destination_arg;
    (void)output; (void)output_length;
    if (OPEN_CFW_CLI_FS_MOUNTED != 1u) return 0;
    source_arg = open_cfw_cli_fs_arg(command, 1u, &source_length);
    destination_arg = open_cfw_cli_fs_arg(command, 2u, &destination_length);
    if (source_arg == NULL || destination_arg == NULL) { OPEN_CFW_CLI_FS_PRINT("mv: missing operand\r\n"); return 0; }
    if (source_length + destination_length >= OPEN_CFW_CLI_FS_PATH_MAX) { OPEN_CFW_CLI_FS_PRINT("mv: parameter too long\r\n"); return 0; }
    if (open_cfw_cli_fs_join(source_joined, sizeof(source_joined), OPEN_CFW_CLI_FS_CWD, source_arg) != 0 || open_cfw_cli_fs_normalize_path(source, source_joined) != 0) {
        OPEN_CFW_CLI_FS_PRINT("mv: invalid source path\r\n"); return 0;
    }
    if (open_cfw_cli_fs_join(destination_joined, sizeof(destination_joined), OPEN_CFW_CLI_FS_CWD, destination_arg) != 0 || open_cfw_cli_fs_normalize_path(destination, destination_joined) != 0) {
        OPEN_CFW_CLI_FS_PRINT("mv: invalid destination path\r\n"); return 0;
    }
    if (OPEN_CFW_CLI_FS_STAT(OPEN_CFW_CLI_FS_VOLUME, source, &source_info) != 0) {
        OPEN_CFW_CLI_FS_PRINT("mv: source file/directory not found\r\n"); return 0;
    }
    if (OPEN_CFW_CLI_FS_STAT(OPEN_CFW_CLI_FS_VOLUME, destination, &destination_info) == 0 && destination_info.type == OPEN_CFW_CLI_FS_TYPE_DIRECTORY) {
        if (open_cfw_cli_fs_join(final_destination, sizeof(final_destination), destination, source_info.name) != 0) return 0;
    } else if (open_cfw_cli_fs_copy(final_destination, sizeof(final_destination), destination) != 0) return 0;
    if (OPEN_CFW_CLI_FS_STAT(OPEN_CFW_CLI_FS_VOLUME, final_destination, &destination_info) == 0) {
        OPEN_CFW_CLI_FS_PRINT("mv: destination already exists\r\n"); return 0;
    }
    if (OPEN_CFW_CLI_FS_RENAME(OPEN_CFW_CLI_FS_VOLUME, source, final_destination) != 0) OPEN_CFW_CLI_FS_PRINT("mv: move/rename failed\r\n");
    return 0;
}
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_MD5_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_cli_fs_md5(char *output, uint32_t output_length, const char *command)
{
    struct open_cfw_cli_fs_info info;
    struct open_cfw_cli_fs_file file;
    struct open_cfw_cli_fs_md5 context;
    uint8_t buffer[OPEN_CFW_CLI_FS_READ_CHUNK];
    uint8_t digest[16];
    char joined[OPEN_CFW_CLI_FS_PATH_MAX];
    char path[OPEN_CFW_CLI_FS_PATH_MAX];
    uint32_t length = 0u;
    const char *name;
    int32_t count;
    uint32_t index;
    (void)output; (void)output_length;
    if (OPEN_CFW_CLI_FS_MOUNTED != 1u) return 0;
    name = open_cfw_cli_fs_arg(command, 1u, &length);
    if (name == NULL) { OPEN_CFW_CLI_FS_PRINT("md5: missing file operand\r\n"); return 0; }
    if (open_cfw_cli_fs_join(joined, sizeof(joined), OPEN_CFW_CLI_FS_CWD, name) != 0 || open_cfw_cli_fs_normalize_path(path, joined) != 0) {
        OPEN_CFW_CLI_FS_PRINT("md5: invalid file path\r\n"); return 0;
    }
    if (OPEN_CFW_CLI_FS_STAT(OPEN_CFW_CLI_FS_VOLUME, path, &info) != 0) { OPEN_CFW_CLI_FS_PRINT("md5: file not found\r\n"); return 0; }
    if (info.type == OPEN_CFW_CLI_FS_TYPE_DIRECTORY) { OPEN_CFW_CLI_FS_PRINT("md5: cannot calculate hash for directory\r\n"); return 0; }
    if (OPEN_CFW_CLI_FS_FILE_OPEN(OPEN_CFW_CLI_FS_VOLUME, &file, path, OPEN_CFW_CLI_FS_O_RDONLY) != 0) { OPEN_CFW_CLI_FS_PRINT("md5: cannot open file\r\n"); return 0; }
    OPEN_CFW_CLI_FS_MD5_INIT(&context);
    while ((count = OPEN_CFW_CLI_FS_FILE_READ(OPEN_CFW_CLI_FS_VOLUME, &file, buffer, sizeof(buffer))) > 0) OPEN_CFW_CLI_FS_MD5_UPDATE(&context, buffer, (uint32_t)count);
    (void)OPEN_CFW_CLI_FS_FILE_CLOSE(OPEN_CFW_CLI_FS_VOLUME, &file);
    if (count < 0) { OPEN_CFW_CLI_FS_PRINT("md5: file read error\r\n"); return 0; }
    OPEN_CFW_CLI_FS_MD5_FINAL(digest, &context);
    OPEN_CFW_CLI_FS_PRINT("MD5(%s) = ", path);
    for (index = 0u; index < sizeof(digest); ++index) OPEN_CFW_CLI_FS_PRINT("%02x", digest[index]);
    OPEN_CFW_CLI_FS_PRINT("\r\n");
    return 0;
}
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_DF_ONLY)
__attribute__((used, noinline)) int32_t open_cfw_cli_fs_df(char *output, uint32_t output_length, const char *command)
{
    int32_t used_blocks;
    uint32_t block_size;
    uint32_t block_count;
    uint32_t total;
    uint32_t used;
    uint32_t available;
    uint32_t percent;
    (void)output; (void)output_length; (void)command;
    if (OPEN_CFW_CLI_FS_MOUNTED != 1u) { OPEN_CFW_CLI_FS_PRINT("Filesystem not mounted\r\n"); return 0; }
    used_blocks = OPEN_CFW_CLI_FS_SIZE(OPEN_CFW_CLI_FS_VOLUME);
    if (used_blocks < 0) { OPEN_CFW_CLI_FS_PRINT("df: lfs_fs_size failed err=%ld\r\n", (long)used_blocks); return 0; }
    block_size = OPEN_CFW_CLI_FS_BLOCK_SIZE(OPEN_CFW_CLI_FS_VOLUME);
    block_count = OPEN_CFW_CLI_FS_BLOCK_COUNT(OPEN_CFW_CLI_FS_VOLUME);
    total = block_size * block_count;
    used = block_size * (uint32_t)used_blocks;
    available = total - used;
    percent = total == 0u ? 0u : (100u * used) / total;
    OPEN_CFW_CLI_FS_PRINT("Filesystem     1K-blocks      Used Available Use%% Mounted on\r\n");
    OPEN_CFW_CLI_FS_PRINT("littlefs   %10lu %9lu %9lu %3lu%% /\r\n", (unsigned long)((total + 1023u) >> 10), (unsigned long)((used + 1023u) >> 10), (unsigned long)((available + 1023u) >> 10), (unsigned long)percent);
    return 0;
}
#endif

#if defined(OPEN_CFW_CLI_FS_BUILD_ALL) || defined(OPEN_CFW_CLI_FS_BLOCK_STATS_ONLY)
__attribute__((used, noinline)) void open_cfw_cli_fs_block_stats_accumulate(uint32_t address, uint32_t size, uint32_t used, struct open_cfw_cli_fs_block_stats *stats)
{
    (void)address;
    if (stats == NULL) return;
    if (used != 0u) {
        stats->used_bytes += size;
        ++stats->used_blocks;
    } else {
        stats->free_bytes += size;
    }
    ++stats->blocks;
}
#endif
