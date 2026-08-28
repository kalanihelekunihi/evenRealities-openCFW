/*
 * SPDX-License-Identifier: MIT
 *
 * Recovered G2 S200 bootloader stream-redirection initialization ABI.
 */

#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_REDIRECT_INIT_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_REDIRECT_INIT_H

typedef __UINT32_TYPE__ open_cfw_bootloader_redirect_u32;
typedef __UINTPTR_TYPE__ open_cfw_bootloader_redirect_uintptr;

typedef void *open_cfw_bootloader_redirect_mutex_id;

enum {
    OPEN_CFW_BOOTLOADER_REDIRECT_LOG_ERROR = 1,
    OPEN_CFW_BOOTLOADER_REDIRECT_LOG_INFO = 3,
    OPEN_CFW_BOOTLOADER_REDIRECT_STDOUT_MUTEX_ADDRESS = 0x2002712CU,
    OPEN_CFW_BOOTLOADER_REDIRECT_STDIN_MUTEX_ADDRESS = 0x20027130U,
    OPEN_CFW_BOOTLOADER_REDIRECT_ERROR_LINE = 0x271U,
    OPEN_CFW_BOOTLOADER_REDIRECT_INFO_LINE = 0x275U
};

#ifndef OPEN_CFW_BOOTLOADER_REDIRECT_MUTEX_NEW
extern open_cfw_bootloader_redirect_mutex_id osMutexNew(
    const void *attributes
);
#define OPEN_CFW_BOOTLOADER_REDIRECT_MUTEX_NEW(attributes) \
    osMutexNew(attributes)
#endif

#ifndef OPEN_CFW_BOOTLOADER_REDIRECT_LOG
extern void elog_output(
    unsigned char level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...
);
#define OPEN_CFW_BOOTLOADER_REDIRECT_LOG( \
    level, tag, file, function, line, format \
) \
    elog_output((level), (tag), (file), (function), (line), (format))
#endif

#ifndef OPEN_CFW_BOOTLOADER_REDIRECT_STDOUT_MUTEX
#define OPEN_CFW_BOOTLOADER_REDIRECT_STDOUT_MUTEX \
    (*(open_cfw_bootloader_redirect_mutex_id volatile *) \
        (open_cfw_bootloader_redirect_uintptr) \
            OPEN_CFW_BOOTLOADER_REDIRECT_STDOUT_MUTEX_ADDRESS)
#endif

#ifndef OPEN_CFW_BOOTLOADER_REDIRECT_STDIN_MUTEX
#define OPEN_CFW_BOOTLOADER_REDIRECT_STDIN_MUTEX \
    (*(open_cfw_bootloader_redirect_mutex_id volatile *) \
        (open_cfw_bootloader_redirect_uintptr) \
            OPEN_CFW_BOOTLOADER_REDIRECT_STDIN_MUTEX_ADDRESS)
#endif

int open_cfw_bootloader_redirect_init(void);

#endif
