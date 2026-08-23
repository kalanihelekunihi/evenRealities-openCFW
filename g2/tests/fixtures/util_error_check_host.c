#include <stdarg.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

const char open_cfw_test_api_format[] = "Error code 0x%04X: %s";
const char open_cfw_test_bool_format[] = "(%s) is not established.";
const char open_cfw_test_log_format[] = "%s, %s %u, %s";
const char open_cfw_test_async_format[] = "[assert]%s, %s %u, %s";
const char open_cfw_test_tag[] = "assert";
const char open_cfw_test_source_file[] = "util_error_check.c";
const char open_cfw_test_handler_name[] = "APP_errorFaultHandler";

const struct open_cfw_util_error_table_row open_cfw_test_error_table[43] = {
    {0u, "Success."}, {1u, "Invalid parameter."},
    [29] = {0x80u, "Application error."},
    [42] = {0x2au, "Not enough credits."},
};

uint32_t open_cfw_test_error_filter;
uint32_t open_cfw_test_sync_count;
uint32_t open_cfw_test_async_count;
uint32_t open_cfw_test_packed;
char open_cfw_test_sync[768];
char open_cfw_test_async[768];

void open_cfw_test_error_reset(void)
{
    open_cfw_test_error_filter = 0u;
    open_cfw_test_sync_count = 0u;
    open_cfw_test_async_count = 0u;
    open_cfw_test_packed = 0u;
    memset(open_cfw_test_sync, 0, sizeof(open_cfw_test_sync));
    memset(open_cfw_test_async, 0, sizeof(open_cfw_test_async));
}

int open_cfw_util_error_format(char *output, const char *format, ...)
{
    int result;
    va_list args;
    va_start(args, format);
    result = vsnprintf(output, 512u, format, args);
    va_end(args);
    return result;
}

uint32_t open_cfw_util_error_filter(void)
{
    return open_cfw_test_error_filter;
}

void open_cfw_util_error_log(
    uint32_t level, const char *tag, const char *file,
    const char *function, long line, const char *format, ...
)
{
    va_list args;
    (void)level;
    (void)tag;
    (void)file;
    (void)function;
    (void)line;
    ++open_cfw_test_sync_count;
    va_start(args, format);
    (void)vsnprintf(open_cfw_test_sync, sizeof(open_cfw_test_sync), format, args);
    va_end(args);
}

void open_cfw_util_error_async_log(uint32_t packed, const char *format, ...)
{
    va_list args;
    open_cfw_test_packed = packed;
    ++open_cfw_test_async_count;
    va_start(args, format);
    (void)vsnprintf(open_cfw_test_async, sizeof(open_cfw_test_async), format, args);
    va_end(args);
}
