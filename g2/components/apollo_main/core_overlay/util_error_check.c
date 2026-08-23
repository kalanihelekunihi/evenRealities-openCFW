/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room G2 adapter for the Goodix GR551x SDK 1.7.0-derived
 * APP_errorFaultHandler at [0x00509B48,0x00509BFA).  The 43-row table and
 * diagnostic strings remain authenticated stock read-only data; only the
 * executable policy is replaced here.
 *
 * Unlike stock, an unknown API error cannot walk beyond the table.  It is
 * rendered with the table's generic "Application error." entry.  This is an
 * intentional fail-safe correction to the recovered unbounded search.
 */

#include <stddef.h>
#include <stdint.h>

void *memset(void *destination, int value, size_t length);

typedef union {
    uint16_t error_code;
    const char *expression;
} open_cfw_util_error_value;

typedef struct __attribute__((packed, aligned(4))) {
    uint8_t error_type;
    uint8_t reserved[3];
    open_cfw_util_error_value value;
    const char *file;
    const char *function;
    uint32_t line;
} open_cfw_util_error_info;

typedef struct {
    uint32_t error_code;
    const char *message;
} open_cfw_util_error_table_row;

#if defined(__arm__)
_Static_assert(offsetof(open_cfw_util_error_info, value) == 4u,
    "stock error value offset changed");
_Static_assert(sizeof(void *) == 4u, "Apollo510 requires 32-bit pointers");
_Static_assert(offsetof(open_cfw_util_error_info, file) == 8u,
    "stock error file offset changed");
_Static_assert(offsetof(open_cfw_util_error_info, function) == 12u,
    "stock error function offset changed");
_Static_assert(offsetof(open_cfw_util_error_info, line) == 16u,
    "stock error line offset changed");
_Static_assert(sizeof(open_cfw_util_error_info) == 20u,
    "stock error-info ABI changed");
_Static_assert(sizeof(open_cfw_util_error_table_row) == 8u,
    "stock error table ABI changed");
#endif

#ifndef OPEN_CFW_UTIL_ERROR_TABLE
#define OPEN_CFW_UTIL_ERROR_TABLE \
    ((const open_cfw_util_error_table_row *)(uintptr_t)0x006c8e60u)
#endif

#ifndef OPEN_CFW_UTIL_ERROR_FORMAT
int open_cfw_util_error_format(char *output, const char *format, ...);
#define OPEN_CFW_UTIL_ERROR_FORMAT(...) open_cfw_util_error_format(__VA_ARGS__)
#endif

#ifndef OPEN_CFW_UTIL_ERROR_FILTER
uint32_t open_cfw_util_error_filter(void);
#define OPEN_CFW_UTIL_ERROR_FILTER() open_cfw_util_error_filter()
#endif

#ifndef OPEN_CFW_UTIL_ERROR_LOG
void open_cfw_util_error_log(
    uint32_t level, const char *tag, const char *file,
    const char *function, long line, const char *format, ...
);
#define OPEN_CFW_UTIL_ERROR_LOG(...) open_cfw_util_error_log(__VA_ARGS__)
#endif

#ifndef OPEN_CFW_UTIL_ERROR_ASYNC_LOG
void open_cfw_util_error_async_log(uint32_t packed, const char *format, ...);
#define OPEN_CFW_UTIL_ERROR_ASYNC_LOG(...) \
    open_cfw_util_error_async_log(__VA_ARGS__)
#endif

#ifndef OPEN_CFW_UTIL_ERROR_API_FORMAT
#define OPEN_CFW_UTIL_ERROR_API_FORMAT \
    ((const char *)(uintptr_t)0x0077d78cu)
#endif
#ifndef OPEN_CFW_UTIL_ERROR_BOOL_FORMAT
#define OPEN_CFW_UTIL_ERROR_BOOL_FORMAT \
    ((const char *)(uintptr_t)0x007746e8u)
#endif
#ifndef OPEN_CFW_UTIL_ERROR_LOG_FORMAT
#define OPEN_CFW_UTIL_ERROR_LOG_FORMAT \
    ((const char *)(uintptr_t)0x00789ef0u)
#endif
#ifndef OPEN_CFW_UTIL_ERROR_ASYNC_FORMAT
#define OPEN_CFW_UTIL_ERROR_ASYNC_FORMAT \
    ((const char *)(uintptr_t)0x0077d7a4u)
#endif
#ifndef OPEN_CFW_UTIL_ERROR_TAG
#define OPEN_CFW_UTIL_ERROR_TAG \
    ((const char *)(uintptr_t)0x0078edc4u)
#endif
#ifndef OPEN_CFW_UTIL_ERROR_SOURCE_FILE
#define OPEN_CFW_UTIL_ERROR_SOURCE_FILE \
    ((const char *)(uintptr_t)0x007086c4u)
#endif
#ifndef OPEN_CFW_UTIL_ERROR_HANDLER_NAME
#define OPEN_CFW_UTIL_ERROR_HANDLER_NAME \
    ((const char *)(uintptr_t)0x0077d774u)
#endif

enum {
    OPEN_CFW_UTIL_ERROR_API_RETURN = 0,
    OPEN_CFW_UTIL_ERROR_BOOL_COMPARE = 1,
    OPEN_CFW_UTIL_ERROR_TABLE_ROWS = 43,
    OPEN_CFW_UTIL_ERROR_APPLICATION_ROW = 29,
};

void open_cfw_app_error_fault_handler(const open_cfw_util_error_info *error)
{
    char rendered[512];
    const open_cfw_util_error_table_row *table = OPEN_CFW_UTIL_ERROR_TABLE;
    uint32_t index;
    uint32_t filter;

    memset(rendered, 0, sizeof(rendered));
    if (error->error_type == OPEN_CFW_UTIL_ERROR_API_RETURN) {
        for (index = 0u; index < OPEN_CFW_UTIL_ERROR_TABLE_ROWS; ++index) {
            if ((uint16_t)table[index].error_code == error->value.error_code) {
                break;
            }
        }
        if (index == OPEN_CFW_UTIL_ERROR_TABLE_ROWS) {
            index = OPEN_CFW_UTIL_ERROR_APPLICATION_ROW;
        }
        (void)OPEN_CFW_UTIL_ERROR_FORMAT(
            rendered, OPEN_CFW_UTIL_ERROR_API_FORMAT,
            (unsigned)error->value.error_code, table[index].message
        );
    } else if (error->error_type == OPEN_CFW_UTIL_ERROR_BOOL_COMPARE) {
        (void)OPEN_CFW_UTIL_ERROR_FORMAT(
            rendered, OPEN_CFW_UTIL_ERROR_BOOL_FORMAT,
            error->value.expression
        );
    }

    filter = OPEN_CFW_UTIL_ERROR_FILTER();
    if ((filter & 2u) != 0u) {
        OPEN_CFW_UTIL_ERROR_LOG(
            1u, OPEN_CFW_UTIL_ERROR_TAG, OPEN_CFW_UTIL_ERROR_SOURCE_FILE,
            OPEN_CFW_UTIL_ERROR_HANDLER_NAME, 113,
            OPEN_CFW_UTIL_ERROR_LOG_FORMAT,
            error->file, error->function, error->line, rendered
        );
    }
    filter = OPEN_CFW_UTIL_ERROR_FILTER();
    if ((filter & 1u) != 0u ||
            (OPEN_CFW_UTIL_ERROR_FILTER() & 4u) != 0u) {
        OPEN_CFW_UTIL_ERROR_ASYNC_LOG(
            0x05000000u, OPEN_CFW_UTIL_ERROR_ASYNC_FORMAT,
            error->file, error->function, error->line, rendered
        );
    }
}
