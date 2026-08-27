/*
 * Copyright (c) 2015-2018, Armink, <armink.ztl@gmail.com>
 * SPDX-License-Identifier: MIT
 *
 * Freestanding adaptation of EasyLogger's output-lock enable transition for
 * the authenticated Even Realities G2 S200 bootloader ABI.
 */

#include "../../shared/easylogger/runtime_easylogger_helpers.h"

typedef open_cfw_easylogger_helpers_u8 open_cfw_bootloader_elog_u8;
typedef open_cfw_easylogger_helpers_uintptr open_cfw_bootloader_elog_uintptr;

enum {
    OPEN_CFW_BOOTLOADER_ELOG_PORT_LOCK_THUMB = 0x0041A69BU,
    OPEN_CFW_BOOTLOADER_ELOG_PORT_UNLOCK_THUMB = 0x0041A6A3U
};

typedef void (*open_cfw_bootloader_elog_void_fn)(void);

#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_LOCK_ENABLED_HOST)
struct open_cfw_easylogger_helpers_logger *
open_cfw_bootloader_easylogger_lock_enabled_host_get_logger(void);
void open_cfw_bootloader_easylogger_lock_enabled_host_port_lock(void);
void open_cfw_bootloader_easylogger_lock_enabled_host_port_unlock(void);
#endif

static __attribute__((always_inline)) inline
struct open_cfw_easylogger_helpers_logger *
open_cfw_bootloader_easylogger_lock_enabled_logger(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_LOCK_ENABLED_HOST)
    return open_cfw_bootloader_easylogger_lock_enabled_host_get_logger();
#else
    return (struct open_cfw_easylogger_helpers_logger *)
        (open_cfw_bootloader_elog_uintptr)
            OPEN_CFW_EASYLOGGER_HELPERS_PROFILE_STATE_ADDRESS;
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_lock_enabled_port_lock(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_LOCK_ENABLED_HOST)
    open_cfw_bootloader_easylogger_lock_enabled_host_port_lock();
#else
    ((open_cfw_bootloader_elog_void_fn)
        (open_cfw_bootloader_elog_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_PORT_LOCK_THUMB)();
#endif
}

static __attribute__((always_inline)) inline void
open_cfw_bootloader_easylogger_lock_enabled_port_unlock(void)
{
#if defined(OPEN_CFW_BOOTLOADER_EASYLOGGER_LOCK_ENABLED_HOST)
    open_cfw_bootloader_easylogger_lock_enabled_host_port_unlock();
#else
    ((open_cfw_bootloader_elog_void_fn)
        (open_cfw_bootloader_elog_uintptr)
            OPEN_CFW_BOOTLOADER_ELOG_PORT_UNLOCK_THUMB)();
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_easylogger_output_lock_enabled_417b7c(
    open_cfw_bootloader_elog_u8 enabled)
{
    struct open_cfw_easylogger_helpers_logger *const logger =
        open_cfw_bootloader_easylogger_lock_enabled_logger();

    logger->output_lock_enabled = enabled;
    if (logger->output_lock_enabled == 0U) {
        return;
    }
    if (logger->output_is_locked_before_disable == 0U &&
            logger->output_is_locked_before_enable != 0U) {
        open_cfw_bootloader_easylogger_lock_enabled_port_lock();
    } else if (logger->output_is_locked_before_disable != 0U &&
            logger->output_is_locked_before_enable == 0U) {
        open_cfw_bootloader_easylogger_lock_enabled_port_unlock();
    }
}
