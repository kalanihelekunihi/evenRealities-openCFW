#ifndef OPEN_CFW_AT_FS_HOST_H
#define OPEN_CFW_AT_FS_HOST_H

#include <stddef.h>
#include <stdint.h>

struct open_cfw_at_fs_dirent;

extern uint32_t open_cfw_test_at_fs_ready;
extern void *open_cfw_test_at_fs_object;

int open_cfw_test_at_fs_remove(const char *path);
void *open_cfw_test_at_fs_opendir(const char *path);
struct open_cfw_at_fs_dirent *open_cfw_test_at_fs_readdir(void *directory);
void open_cfw_test_at_fs_closedir(void *directory);
int open_cfw_test_at_fs_strcmp(const char *left, const char *right);
void *open_cfw_test_at_fs_memset(void *target, int value, size_t size);
int open_cfw_test_at_fs_format(char *target, const char *format, ...);
void open_cfw_test_at_fs_append(char *target, const char *suffix);
int open_cfw_test_at_fs_delay(uint32_t ticks);
void *open_cfw_test_at_fs_open(const void *path, const char *mode);
int open_cfw_test_at_fs_seek(void *stream, int offset, unsigned int origin);
int open_cfw_test_at_fs_tell(void *stream);
void open_cfw_test_at_fs_close(void *stream);
int open_cfw_test_at_fs_mkdir(void *filesystem, const char *path);
void open_cfw_test_at_fs_output(const char *format, ...);

#define OPEN_CFW_AT_FS_READY open_cfw_test_at_fs_ready
#define OPEN_CFW_AT_FS_OBJECT open_cfw_test_at_fs_object
#define OPEN_CFW_AT_FS_REMOVE(path) open_cfw_test_at_fs_remove((path))
#define OPEN_CFW_AT_FS_OPENDIR(path) open_cfw_test_at_fs_opendir((path))
#define OPEN_CFW_AT_FS_READDIR(directory) open_cfw_test_at_fs_readdir((directory))
#define OPEN_CFW_AT_FS_CLOSEDIR(directory) open_cfw_test_at_fs_closedir((directory))
#define OPEN_CFW_AT_FS_STRCMP(left, right) open_cfw_test_at_fs_strcmp((left), (right))
#define OPEN_CFW_AT_FS_MEMSET(target, value, size) \
    open_cfw_test_at_fs_memset((target), (value), (size))
#define OPEN_CFW_AT_FS_FORMAT(...) open_cfw_test_at_fs_format(__VA_ARGS__)
#define OPEN_CFW_AT_FS_APPEND(target, suffix) open_cfw_test_at_fs_append((target), (suffix))
#define OPEN_CFW_AT_FS_DELAY(ticks) open_cfw_test_at_fs_delay((ticks))
#define OPEN_CFW_AT_FS_OPEN(path, mode) open_cfw_test_at_fs_open((path), (mode))
#define OPEN_CFW_AT_FS_SEEK(stream, offset, origin) \
    open_cfw_test_at_fs_seek((stream), (offset), (origin))
#define OPEN_CFW_AT_FS_TELL(stream) open_cfw_test_at_fs_tell((stream))
#define OPEN_CFW_AT_FS_CLOSE(stream) open_cfw_test_at_fs_close((stream))
#define OPEN_CFW_AT_FS_MKDIR(filesystem, path) \
    open_cfw_test_at_fs_mkdir((filesystem), (path))
#define OPEN_CFW_AT_FS_OUTPUT(...) open_cfw_test_at_fs_output(__VA_ARGS__)

#define OPEN_CFW_AT_FS_RM_ERROR_ADDRESS ((uintptr_t)"RMERR %s %d")
#define OPEN_CFW_AT_FS_RM_OK_ADDRESS ((uintptr_t)"RM+OK")
#define OPEN_CFW_AT_FS_OPEN_ERROR_ADDRESS ((uintptr_t)"OPENERR %s")
#define OPEN_CFW_AT_FS_DIRECTORY_ADDRESS ((uintptr_t)"D %s")
#define OPEN_CFW_AT_FS_FILE_ADDRESS ((uintptr_t)"F %s %d %d")
#define OPEN_CFW_AT_FS_LS_OK_ADDRESS ((uintptr_t)"LS+OK")
#define OPEN_CFW_AT_FS_LS_ERROR_ADDRESS ((uintptr_t)"LS+ERR")
#define OPEN_CFW_AT_FS_MKDIR_ERROR_ADDRESS ((uintptr_t)"MKDIRERR %s")
#define OPEN_CFW_AT_FS_MKDIR_OK_ADDRESS ((uintptr_t)"MKDIR+OK")
#define OPEN_CFW_AT_FS_DOT_ADDRESS ((uintptr_t)".")
#define OPEN_CFW_AT_FS_DOT_DOT_ADDRESS ((uintptr_t)"..")
#define OPEN_CFW_AT_FS_CHILD_FORMAT_ADDRESS ((uintptr_t)"%s/")
#define OPEN_CFW_AT_FS_READ_MODE_ADDRESS ((uintptr_t)"r")

#endif
