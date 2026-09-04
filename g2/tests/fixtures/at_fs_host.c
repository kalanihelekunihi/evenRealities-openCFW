#include "at_fs_host.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

struct open_cfw_at_fs_dirent {
    char name[0x100];
    uint8_t type;
};

struct test_directory {
    unsigned int index;
    unsigned int count;
    struct open_cfw_at_fs_dirent entries[4];
};

uint32_t open_cfw_test_at_fs_ready;
void *open_cfw_test_at_fs_object = (void *)(uintptr_t)0x1234u;
int open_cfw_test_at_fs_remove_result;
int open_cfw_test_at_fs_mkdir_result;
unsigned int open_cfw_test_at_fs_delay_count;
unsigned int open_cfw_test_at_fs_close_count;
unsigned int open_cfw_test_at_fs_closedir_count;
unsigned int open_cfw_test_at_fs_output_count;
char open_cfw_test_at_fs_outputs[16][160];
static struct test_directory root_directory;
static struct test_directory sub_directory;
static int root_stream;
static int nested_stream;

static void set_entry(
    struct open_cfw_at_fs_dirent *entry, const char *name, uint8_t type
)
{
    (void)snprintf(entry->name, sizeof(entry->name), "%s", name);
    entry->type = type;
}

void open_cfw_test_at_fs_reset(void)
{
    memset(&root_directory, 0, sizeof(root_directory));
    memset(&sub_directory, 0, sizeof(sub_directory));
    memset(open_cfw_test_at_fs_outputs, 0, sizeof(open_cfw_test_at_fs_outputs));
    set_entry(&root_directory.entries[0], ".", 4u);
    set_entry(&root_directory.entries[1], "..", 4u);
    set_entry(&root_directory.entries[2], "sub", 4u);
    set_entry(&root_directory.entries[3], "file", 0u);
    root_directory.count = 4u;
    set_entry(&sub_directory.entries[0], "nested", 0u);
    sub_directory.count = 1u;
    open_cfw_test_at_fs_ready = 1u;
    open_cfw_test_at_fs_remove_result = 0;
    open_cfw_test_at_fs_mkdir_result = 0;
    open_cfw_test_at_fs_delay_count = 0u;
    open_cfw_test_at_fs_close_count = 0u;
    open_cfw_test_at_fs_closedir_count = 0u;
    open_cfw_test_at_fs_output_count = 0u;
}

int open_cfw_test_at_fs_remove(const char *path)
{
    (void)path;
    return open_cfw_test_at_fs_remove_result;
}

void *open_cfw_test_at_fs_opendir(const char *path)
{
    if (strcmp(path, "root") == 0) {
        root_directory.index = 0u;
        return &root_directory;
    }
    if (strcmp(path, "root/sub") == 0) {
        sub_directory.index = 0u;
        return &sub_directory;
    }
    return NULL;
}

struct open_cfw_at_fs_dirent *open_cfw_test_at_fs_readdir(void *directory)
{
    struct test_directory *value = directory;
    if (value->index == value->count) {
        return NULL;
    }
    return &value->entries[value->index++];
}

void open_cfw_test_at_fs_closedir(void *directory)
{
    (void)directory;
    ++open_cfw_test_at_fs_closedir_count;
}

int open_cfw_test_at_fs_strcmp(const char *left, const char *right)
{
    return strcmp(left, right);
}

void *open_cfw_test_at_fs_memset(void *target, int value, size_t size)
{
    return memset(target, value, size);
}

int open_cfw_test_at_fs_format(char *target, const char *format, ...)
{
    int result;
    va_list arguments;
    va_start(arguments, format);
    result = vsnprintf(target, 0x81u, format, arguments);
    va_end(arguments);
    return result;
}

void open_cfw_test_at_fs_append(char *target, const char *suffix)
{
    (void)strncat(target, suffix, 0x80u - strlen(target));
}

int open_cfw_test_at_fs_delay(uint32_t ticks)
{
    if (ticks == 30u) {
        ++open_cfw_test_at_fs_delay_count;
    }
    return 0;
}

void *open_cfw_test_at_fs_open(const void *path, const char *mode)
{
    (void)mode;
    if (strcmp(path, "root/file") == 0) {
        return &root_stream;
    }
    if (strcmp(path, "root/sub/nested") == 0) {
        return &nested_stream;
    }
    return NULL;
}

int open_cfw_test_at_fs_seek(void *stream, int offset, unsigned int origin)
{
    (void)stream;
    return (offset == 0 && origin == 2u) ? 0 : -1;
}

int open_cfw_test_at_fs_tell(void *stream)
{
    return stream == &root_stream ? 2050 : 1023;
}

void open_cfw_test_at_fs_close(void *stream)
{
    (void)stream;
    ++open_cfw_test_at_fs_close_count;
}

int open_cfw_test_at_fs_mkdir(void *filesystem, const char *path)
{
    (void)path;
    if (filesystem != open_cfw_test_at_fs_object) {
        return -99;
    }
    return open_cfw_test_at_fs_mkdir_result;
}

void open_cfw_test_at_fs_output(const char *format, ...)
{
    va_list arguments;
    unsigned int index = open_cfw_test_at_fs_output_count++;
    va_start(arguments, format);
    (void)vsnprintf(open_cfw_test_at_fs_outputs[index], 160u, format, arguments);
    va_end(arguments);
}
