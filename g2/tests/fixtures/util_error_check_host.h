#ifndef OPEN_CFW_UTIL_ERROR_CHECK_HOST_H
#define OPEN_CFW_UTIL_ERROR_CHECK_HOST_H

#include <stdint.h>

struct open_cfw_util_error_table_row {
    uint32_t error_code;
    const char *message;
};

extern const struct open_cfw_util_error_table_row open_cfw_test_error_table[43];
extern const char open_cfw_test_api_format[];
extern const char open_cfw_test_bool_format[];
extern const char open_cfw_test_log_format[];
extern const char open_cfw_test_async_format[];
extern const char open_cfw_test_tag[];
extern const char open_cfw_test_source_file[];
extern const char open_cfw_test_handler_name[];

#define OPEN_CFW_UTIL_ERROR_TABLE \
    ((const open_cfw_util_error_table_row *)(const void *) \
        open_cfw_test_error_table)
#define OPEN_CFW_UTIL_ERROR_API_FORMAT open_cfw_test_api_format
#define OPEN_CFW_UTIL_ERROR_BOOL_FORMAT open_cfw_test_bool_format
#define OPEN_CFW_UTIL_ERROR_LOG_FORMAT open_cfw_test_log_format
#define OPEN_CFW_UTIL_ERROR_ASYNC_FORMAT open_cfw_test_async_format
#define OPEN_CFW_UTIL_ERROR_TAG open_cfw_test_tag
#define OPEN_CFW_UTIL_ERROR_SOURCE_FILE open_cfw_test_source_file
#define OPEN_CFW_UTIL_ERROR_HANDLER_NAME open_cfw_test_handler_name

#endif
