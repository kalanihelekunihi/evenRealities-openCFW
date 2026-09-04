/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room reconstruction of platform/service/eAT/at_fs.c from the
 * authenticated G2 2.2.6.10 command records and control-flow.  Diagnostic
 * EasyLogger calls are intentionally omitted; command responses, filesystem
 * readiness gating, traversal, pacing, and return values remain functional.
 */

#include <stddef.h>
#include <stdint.h>

#include "at_fs.h"

struct open_cfw_at_fs_dirent {
    char name[0x100];
    uint8_t type;
};

_Static_assert(
    offsetof(struct open_cfw_at_fs_dirent, type) == 0x100,
    "directory-entry ABI drift"
);

#ifndef OPEN_CFW_AT_FS_READY
#define OPEN_CFW_AT_FS_READY \
    (*(volatile uint32_t *)(uintptr_t)0x200746a8u)
#endif
#ifndef OPEN_CFW_AT_FS_OBJECT
#define OPEN_CFW_AT_FS_OBJECT ((void *)(uintptr_t)0x20071ac8u)
#endif

#ifndef OPEN_CFW_AT_FS_REMOVE
int open_cfw_retained_at_fs_remove(const char *path);
#define OPEN_CFW_AT_FS_REMOVE(path) open_cfw_retained_at_fs_remove((path))
#endif
#ifndef OPEN_CFW_AT_FS_OPENDIR
void *open_cfw_retained_at_fs_opendir(const char *path);
#define OPEN_CFW_AT_FS_OPENDIR(path) open_cfw_retained_at_fs_opendir((path))
#endif
#ifndef OPEN_CFW_AT_FS_READDIR
struct open_cfw_at_fs_dirent *open_cfw_retained_at_fs_readdir(void *directory);
#define OPEN_CFW_AT_FS_READDIR(directory) \
    open_cfw_retained_at_fs_readdir((directory))
#endif
#ifndef OPEN_CFW_AT_FS_CLOSEDIR
void open_cfw_retained_at_fs_closedir(void *directory);
#define OPEN_CFW_AT_FS_CLOSEDIR(directory) \
    open_cfw_retained_at_fs_closedir((directory))
#endif
#ifndef OPEN_CFW_AT_FS_STRCMP
int open_cfw_retained_at_fs_strcmp(const char *left, const char *right);
#define OPEN_CFW_AT_FS_STRCMP(left, right) \
    open_cfw_retained_at_fs_strcmp((left), (right))
#endif
#ifndef OPEN_CFW_AT_FS_MEMSET
void *open_cfw_retained_at_fs_memset(void *target, int value, size_t size);
#define OPEN_CFW_AT_FS_MEMSET(target, value, size) \
    open_cfw_retained_at_fs_memset((target), (value), (size))
#endif
#ifndef OPEN_CFW_AT_FS_FORMAT
int open_cfw_retained_at_fs_format(char *target, const char *format, ...);
#define OPEN_CFW_AT_FS_FORMAT(...) open_cfw_retained_at_fs_format(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_AT_FS_APPEND
void open_cfw_retained_at_fs_append(char *target, const char *suffix);
#define OPEN_CFW_AT_FS_APPEND(target, suffix) \
    open_cfw_retained_at_fs_append((target), (suffix))
#endif
#ifndef OPEN_CFW_AT_FS_DELAY
int open_cfw_retained_at_fs_delay(uint32_t ticks);
#define OPEN_CFW_AT_FS_DELAY(ticks) open_cfw_retained_at_fs_delay((ticks))
#endif
#ifndef OPEN_CFW_AT_FS_OPEN
void *open_cfw_retained_at_fs_open(const void *path, const char *mode);
#define OPEN_CFW_AT_FS_OPEN(path, mode) \
    open_cfw_retained_at_fs_open((path), (mode))
#endif
#ifndef OPEN_CFW_AT_FS_SEEK
int open_cfw_retained_at_fs_seek(void *stream, int offset, unsigned int origin);
#define OPEN_CFW_AT_FS_SEEK(stream, offset, origin) \
    open_cfw_retained_at_fs_seek((stream), (offset), (origin))
#endif
#ifndef OPEN_CFW_AT_FS_TELL
int open_cfw_retained_at_fs_tell(void *stream);
#define OPEN_CFW_AT_FS_TELL(stream) open_cfw_retained_at_fs_tell((stream))
#endif
#ifndef OPEN_CFW_AT_FS_CLOSE
void open_cfw_retained_at_fs_close(void *stream);
#define OPEN_CFW_AT_FS_CLOSE(stream) open_cfw_retained_at_fs_close((stream))
#endif
#ifndef OPEN_CFW_AT_FS_MKDIR
int open_cfw_retained_at_fs_mkdir(void *filesystem, const char *path);
#define OPEN_CFW_AT_FS_MKDIR(filesystem, path) \
    open_cfw_retained_at_fs_mkdir((filesystem), (path))
#endif
#ifndef OPEN_CFW_AT_FS_OUTPUT
void open_cfw_retained_at_fs_output(const char *format, ...);
#define OPEN_CFW_AT_FS_OUTPUT(...) open_cfw_retained_at_fs_output(__VA_ARGS__)
#endif

#ifndef OPEN_CFW_AT_FS_RM_ERROR_ADDRESS
#define OPEN_CFW_AT_FS_RM_ERROR_ADDRESS 0x00752394u
#endif
#ifndef OPEN_CFW_AT_FS_RM_OK_ADDRESS
#define OPEN_CFW_AT_FS_RM_OK_ADDRESS 0x0078cbe4u
#endif
#ifndef OPEN_CFW_AT_FS_OPEN_ERROR_ADDRESS
#define OPEN_CFW_AT_FS_OPEN_ERROR_ADDRESS 0x00769b30u
#endif
#ifndef OPEN_CFW_AT_FS_DIRECTORY_ADDRESS
#define OPEN_CFW_AT_FS_DIRECTORY_ADDRESS 0x0078cbecu
#endif
#ifndef OPEN_CFW_AT_FS_FILE_ADDRESS
#define OPEN_CFW_AT_FS_FILE_ADDRESS 0x007755fcu
#endif
#ifndef OPEN_CFW_AT_FS_LS_OK_ADDRESS
#define OPEN_CFW_AT_FS_LS_OK_ADDRESS 0x0078cbf4u
#endif
#ifndef OPEN_CFW_AT_FS_LS_ERROR_ADDRESS
#define OPEN_CFW_AT_FS_LS_ERROR_ADDRESS 0x0078a37cu
#endif
#ifndef OPEN_CFW_AT_FS_MKDIR_ERROR_ADDRESS
#define OPEN_CFW_AT_FS_MKDIR_ERROR_ADDRESS 0x0075e230u
#endif
#ifndef OPEN_CFW_AT_FS_MKDIR_OK_ADDRESS
#define OPEN_CFW_AT_FS_MKDIR_OK_ADDRESS 0x0078a388u
#endif
#ifndef OPEN_CFW_AT_FS_DOT_ADDRESS
#define OPEN_CFW_AT_FS_DOT_ADDRESS 0x005a56d0u
#endif
#ifndef OPEN_CFW_AT_FS_DOT_DOT_ADDRESS
#define OPEN_CFW_AT_FS_DOT_DOT_ADDRESS 0x005a56d4u
#endif
#ifndef OPEN_CFW_AT_FS_CHILD_FORMAT_ADDRESS
#define OPEN_CFW_AT_FS_CHILD_FORMAT_ADDRESS 0x005a56d8u
#endif
#ifndef OPEN_CFW_AT_FS_READ_MODE_ADDRESS
#define OPEN_CFW_AT_FS_READ_MODE_ADDRESS 0x005a56dcu
#endif

#define OPEN_CFW_AT_FS_STRING(address) ((const char *)(uintptr_t)(address))
#define OPEN_CFW_AT_FS_RM_ERROR \
    OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_RM_ERROR_ADDRESS)
#define OPEN_CFW_AT_FS_RM_OK OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_RM_OK_ADDRESS)
#define OPEN_CFW_AT_FS_OPEN_ERROR \
    OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_OPEN_ERROR_ADDRESS)
#define OPEN_CFW_AT_FS_DIRECTORY \
    OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_DIRECTORY_ADDRESS)
#define OPEN_CFW_AT_FS_FILE OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_FILE_ADDRESS)
#define OPEN_CFW_AT_FS_LS_OK OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_LS_OK_ADDRESS)
#define OPEN_CFW_AT_FS_LS_ERROR \
    OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_LS_ERROR_ADDRESS)
#define OPEN_CFW_AT_FS_MKDIR_ERROR \
    OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_MKDIR_ERROR_ADDRESS)
#define OPEN_CFW_AT_FS_MKDIR_OK \
    OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_MKDIR_OK_ADDRESS)
#define OPEN_CFW_AT_FS_DOT OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_DOT_ADDRESS)
#define OPEN_CFW_AT_FS_DOT_DOT \
    OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_DOT_DOT_ADDRESS)
#define OPEN_CFW_AT_FS_CHILD_FORMAT \
    OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_CHILD_FORMAT_ADDRESS)
#define OPEN_CFW_AT_FS_READ_MODE \
    OPEN_CFW_AT_FS_STRING(OPEN_CFW_AT_FS_READ_MODE_ADDRESS)

#if defined(OPEN_CFW_AT_FS_REMOVE_ONLY)
#define OPEN_CFW_AT_FS_SELECTOR 1
#elif defined(OPEN_CFW_AT_FS_LIST_RECURSIVE_ONLY)
#define OPEN_CFW_AT_FS_SELECTOR 2
#elif defined(OPEN_CFW_AT_FS_LIST_ONLY)
#define OPEN_CFW_AT_FS_SELECTOR 3
#elif defined(OPEN_CFW_AT_FS_MKDIR_ONLY)
#define OPEN_CFW_AT_FS_SELECTOR 4
#else
#define OPEN_CFW_AT_FS_SELECTOR 0
#endif

#if OPEN_CFW_AT_FS_SELECTOR == 0 || OPEN_CFW_AT_FS_SELECTOR == 1
int open_cfw_at_fs_remove(const char *path)
{
    int result;

    if (OPEN_CFW_AT_FS_READY != 1u) {
        return 0;
    }
    result = OPEN_CFW_AT_FS_REMOVE(path);
    if (result != 0) {
        OPEN_CFW_AT_FS_OUTPUT(OPEN_CFW_AT_FS_RM_ERROR, path, result);
        return 0;
    }
    OPEN_CFW_AT_FS_OUTPUT(OPEN_CFW_AT_FS_RM_OK);
    return 1;
}
#endif

#if OPEN_CFW_AT_FS_SELECTOR == 0 || OPEN_CFW_AT_FS_SELECTOR == 2
int open_cfw_at_fs_list_recursive(const char *path)
{
    char child[0x81];
    void *directory;
    struct open_cfw_at_fs_dirent *entry;

    if (OPEN_CFW_AT_FS_READY != 1u) {
        return 0;
    }
    directory = OPEN_CFW_AT_FS_OPENDIR(path);
    if (directory == NULL) {
        OPEN_CFW_AT_FS_OUTPUT(OPEN_CFW_AT_FS_OPEN_ERROR, path);
        return 0;
    }

    OPEN_CFW_AT_FS_MEMSET(child, 0, sizeof(child));
    while ((entry = OPEN_CFW_AT_FS_READDIR(directory)) != NULL) {
        void *stream;
        int size = 0;

        if (OPEN_CFW_AT_FS_STRCMP(entry->name, OPEN_CFW_AT_FS_DOT) == 0 ||
            OPEN_CFW_AT_FS_STRCMP(entry->name, OPEN_CFW_AT_FS_DOT_DOT) == 0) {
            continue;
        }
        OPEN_CFW_AT_FS_FORMAT(child, OPEN_CFW_AT_FS_CHILD_FORMAT, path);
        OPEN_CFW_AT_FS_APPEND(child, entry->name);
        if (entry->type == 4u) {
            (void)OPEN_CFW_AT_FS_DELAY(30u);
            OPEN_CFW_AT_FS_OUTPUT(OPEN_CFW_AT_FS_DIRECTORY, child);
            (void)open_cfw_at_fs_list_recursive(child);
            continue;
        }

        (void)OPEN_CFW_AT_FS_DELAY(30u);
        stream = OPEN_CFW_AT_FS_OPEN(child, OPEN_CFW_AT_FS_READ_MODE);
        if (stream != NULL) {
            (void)OPEN_CFW_AT_FS_SEEK(stream, 0, 2u);
            size = OPEN_CFW_AT_FS_TELL(stream);
            OPEN_CFW_AT_FS_CLOSE(stream);
        }
        OPEN_CFW_AT_FS_OUTPUT(OPEN_CFW_AT_FS_FILE, child, size, size / 0x400);
    }
    OPEN_CFW_AT_FS_CLOSEDIR(directory);
    return 1;
}
#endif

#if OPEN_CFW_AT_FS_SELECTOR == 0 || OPEN_CFW_AT_FS_SELECTOR == 3
int open_cfw_at_fs_list(const char *path)
{
    int result = open_cfw_at_fs_list_recursive(path);

    (void)OPEN_CFW_AT_FS_DELAY(30u);
    OPEN_CFW_AT_FS_OUTPUT(result != 0 ? OPEN_CFW_AT_FS_LS_OK
                                     : OPEN_CFW_AT_FS_LS_ERROR);
    return 1;
}
#endif

#if OPEN_CFW_AT_FS_SELECTOR == 0 || OPEN_CFW_AT_FS_SELECTOR == 4
int open_cfw_at_fs_mkdir(const char *path)
{
    if (OPEN_CFW_AT_FS_READY != 1u) {
        return 0;
    }
    if (OPEN_CFW_AT_FS_MKDIR(OPEN_CFW_AT_FS_OBJECT, path) != 0) {
        OPEN_CFW_AT_FS_OUTPUT(OPEN_CFW_AT_FS_MKDIR_ERROR, path);
    } else {
        OPEN_CFW_AT_FS_OUTPUT(OPEN_CFW_AT_FS_MKDIR_OK);
    }
    return 1;
}
#endif
