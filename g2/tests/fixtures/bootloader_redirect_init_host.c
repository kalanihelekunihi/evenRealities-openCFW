#include <stdint.h>

#include "../../components/bootloader/core_overlay/runtime_redirect_init.h"

static void *open_cfw_redirect_fixture_results[2];
static unsigned int open_cfw_redirect_fixture_create_count;
static void *open_cfw_redirect_fixture_stdout_mutex;
static void *open_cfw_redirect_fixture_stdin_mutex;
static unsigned int open_cfw_redirect_fixture_log_count;
static unsigned int open_cfw_redirect_fixture_log_level;
static long open_cfw_redirect_fixture_log_line;
static const char *open_cfw_redirect_fixture_log_tag;
static const char *open_cfw_redirect_fixture_log_file;
static const char *open_cfw_redirect_fixture_log_function;
static const char *open_cfw_redirect_fixture_log_message;

static void *open_cfw_redirect_fixture_mutex_new(const void *attributes)
{
    unsigned int index = open_cfw_redirect_fixture_create_count;
    (void)attributes;
    open_cfw_redirect_fixture_create_count++;
    return index < 2U ? open_cfw_redirect_fixture_results[index] : (void *)0;
}

static void open_cfw_redirect_fixture_log(
    unsigned char level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *message
)
{
    open_cfw_redirect_fixture_log_count++;
    open_cfw_redirect_fixture_log_level = level;
    open_cfw_redirect_fixture_log_tag = tag;
    open_cfw_redirect_fixture_log_file = file;
    open_cfw_redirect_fixture_log_function = function;
    open_cfw_redirect_fixture_log_line = line;
    open_cfw_redirect_fixture_log_message = message;
}

#undef OPEN_CFW_BOOTLOADER_REDIRECT_MUTEX_NEW
#define OPEN_CFW_BOOTLOADER_REDIRECT_MUTEX_NEW(attributes) \
    open_cfw_redirect_fixture_mutex_new(attributes)
#undef OPEN_CFW_BOOTLOADER_REDIRECT_LOG
#define OPEN_CFW_BOOTLOADER_REDIRECT_LOG( \
    level, tag, file, function, line, format \
) \
    open_cfw_redirect_fixture_log( \
        (level), (tag), (file), (function), (line), (format) \
    )
#undef OPEN_CFW_BOOTLOADER_REDIRECT_STDOUT_MUTEX
#define OPEN_CFW_BOOTLOADER_REDIRECT_STDOUT_MUTEX \
    open_cfw_redirect_fixture_stdout_mutex
#undef OPEN_CFW_BOOTLOADER_REDIRECT_STDIN_MUTEX
#define OPEN_CFW_BOOTLOADER_REDIRECT_STDIN_MUTEX \
    open_cfw_redirect_fixture_stdin_mutex

#include "../../components/bootloader/core_overlay/runtime_redirect_init.c"

void open_cfw_redirect_fixture_reset(uintptr_t first, uintptr_t second)
{
    open_cfw_redirect_fixture_results[0] = (void *)first;
    open_cfw_redirect_fixture_results[1] = (void *)second;
    open_cfw_redirect_fixture_create_count = 0U;
    open_cfw_redirect_fixture_stdout_mutex = (void *)0;
    open_cfw_redirect_fixture_stdin_mutex = (void *)0;
    open_cfw_redirect_fixture_log_count = 0U;
    open_cfw_redirect_fixture_log_level = 0U;
    open_cfw_redirect_fixture_log_line = 0;
    open_cfw_redirect_fixture_log_tag = (const char *)0;
    open_cfw_redirect_fixture_log_file = (const char *)0;
    open_cfw_redirect_fixture_log_function = (const char *)0;
    open_cfw_redirect_fixture_log_message = (const char *)0;
}

int open_cfw_redirect_fixture_call(void)
{
    return open_cfw_bootloader_redirect_init();
}

unsigned int open_cfw_redirect_fixture_create_calls(void)
{
    return open_cfw_redirect_fixture_create_count;
}

uintptr_t open_cfw_redirect_fixture_stdout(void)
{
    return (uintptr_t)open_cfw_redirect_fixture_stdout_mutex;
}

uintptr_t open_cfw_redirect_fixture_stdin(void)
{
    return (uintptr_t)open_cfw_redirect_fixture_stdin_mutex;
}

unsigned int open_cfw_redirect_fixture_log_calls(void)
{
    return open_cfw_redirect_fixture_log_count;
}

unsigned int open_cfw_redirect_fixture_level(void)
{
    return open_cfw_redirect_fixture_log_level;
}

long open_cfw_redirect_fixture_line(void)
{
    return open_cfw_redirect_fixture_log_line;
}

const char *open_cfw_redirect_fixture_tag(void)
{
    return open_cfw_redirect_fixture_log_tag;
}

const char *open_cfw_redirect_fixture_file(void)
{
    return open_cfw_redirect_fixture_log_file;
}

const char *open_cfw_redirect_fixture_function(void)
{
    return open_cfw_redirect_fixture_log_function;
}

const char *open_cfw_redirect_fixture_message(void)
{
    return open_cfw_redirect_fixture_log_message;
}
