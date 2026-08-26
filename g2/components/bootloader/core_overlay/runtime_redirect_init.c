/*
 * SPDX-License-Identifier: GPL-3.0-or-later
 *
 * Clean-room functional recovery of product/s200/bootloader/config/redirect.c
 * redirect_init() from the authenticated G2 2.2.6.10 bootloader.  The body
 * owns only the two-mutex initialization entry.  The adjacent IAR FILE
 * wrappers remain outside this source boundary.
 */

#include "runtime_redirect_init.h"

#ifndef OPEN_CFW_BOOTLOADER_REDIRECT_STDOUT_MUTEX
#error "redirect stdout mutex binding disappeared"
#endif

#ifndef OPEN_CFW_BOOTLOADER_REDIRECT_STDIN_MUTEX
#error "redirect stdin mutex binding disappeared"
#endif

#define OPEN_CFW_BOOTLOADER_REDIRECT_TAG "redirect"
#define OPEN_CFW_BOOTLOADER_REDIRECT_FILE \
    "product\\s200\\bootloader\\config\\redirect.c"
#define OPEN_CFW_BOOTLOADER_REDIRECT_FUNCTION "redirect_init"
#define OPEN_CFW_BOOTLOADER_REDIRECT_CREATE_ERROR \
    "Failed to create redirect mutex for IAR."
#define OPEN_CFW_BOOTLOADER_REDIRECT_READY \
    "redirect init with mutex protection."

__attribute__((used, noinline))
int open_cfw_bootloader_redirect_init(void)
{
    open_cfw_bootloader_redirect_mutex_id stdout_mutex;
    open_cfw_bootloader_redirect_mutex_id stdin_mutex;

    stdout_mutex = OPEN_CFW_BOOTLOADER_REDIRECT_MUTEX_NEW((const void *)0);
    OPEN_CFW_BOOTLOADER_REDIRECT_STDOUT_MUTEX = stdout_mutex;

    stdin_mutex = OPEN_CFW_BOOTLOADER_REDIRECT_MUTEX_NEW((const void *)0);
    OPEN_CFW_BOOTLOADER_REDIRECT_STDIN_MUTEX = stdin_mutex;

    if (stdout_mutex == (open_cfw_bootloader_redirect_mutex_id)0 ||
        stdin_mutex == (open_cfw_bootloader_redirect_mutex_id)0) {
        OPEN_CFW_BOOTLOADER_REDIRECT_LOG(
            OPEN_CFW_BOOTLOADER_REDIRECT_LOG_ERROR,
            OPEN_CFW_BOOTLOADER_REDIRECT_TAG,
            OPEN_CFW_BOOTLOADER_REDIRECT_FILE,
            OPEN_CFW_BOOTLOADER_REDIRECT_FUNCTION,
            OPEN_CFW_BOOTLOADER_REDIRECT_ERROR_LINE,
            OPEN_CFW_BOOTLOADER_REDIRECT_CREATE_ERROR
        );
        return -1;
    }

    OPEN_CFW_BOOTLOADER_REDIRECT_LOG(
        OPEN_CFW_BOOTLOADER_REDIRECT_LOG_INFO,
        OPEN_CFW_BOOTLOADER_REDIRECT_TAG,
        OPEN_CFW_BOOTLOADER_REDIRECT_FILE,
        OPEN_CFW_BOOTLOADER_REDIRECT_FUNCTION,
        OPEN_CFW_BOOTLOADER_REDIRECT_INFO_LINE,
        OPEN_CFW_BOOTLOADER_REDIRECT_READY
    );
    return 0;
}
