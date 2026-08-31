/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_EM9305_RUNTIME_QPC_PORT_H
#define OPEN_CFW_EM9305_RUNTIME_QPC_PORT_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

enum open_cfw_em9305_qpc_port_fault {
    OPEN_CFW_EM9305_QPC_PORT_FAULT_NONE = 0,
    OPEN_CFW_EM9305_QPC_PORT_FAULT_NOT_CONFIGURED = 1,
    OPEN_CFW_EM9305_QPC_PORT_FAULT_QP_ASSERT = 2,
    OPEN_CFW_EM9305_QPC_PORT_FAULT_UNSUPPORTED_TICK = 3
};

typedef uint32_t (*open_cfw_em9305_qpc_critical_entry_fn)(void *context);
typedef void (*open_cfw_em9305_qpc_critical_exit_fn)(void *context,
                                                      uint32_t status);
typedef void (*open_cfw_em9305_qpc_interrupt_fn)(void *context);
typedef uint32_t (*open_cfw_em9305_qpc_isr_context_fn)(void *context);
typedef void (*open_cfw_em9305_qpc_lifecycle_fn)(void *context);
typedef void (*open_cfw_em9305_qpc_assert_fn)(void *context,
                                              const char *module,
                                              int32_t location);

struct open_cfw_em9305_qpc_port_providers {
    void *context;
    open_cfw_em9305_qpc_critical_entry_fn critical_entry;
    open_cfw_em9305_qpc_critical_exit_fn critical_exit;
    open_cfw_em9305_qpc_interrupt_fn interrupt_disable;
    open_cfw_em9305_qpc_interrupt_fn interrupt_enable;
    open_cfw_em9305_qpc_isr_context_fn isr_context;
    open_cfw_em9305_qpc_lifecycle_fn startup;
    open_cfw_em9305_qpc_lifecycle_fn cleanup;
    open_cfw_em9305_qpc_lifecycle_fn idle;
    open_cfw_em9305_qpc_assert_fn assertion;
};

/*
 * Installs the complete board-provider table before QF_init().  The table is
 * copied, so its carrier may be temporary; provider context ownership remains
 * with the caller.  Cleanup is optional.  Every other callback is required.
 */
int32_t open_cfw_em9305_qpc_port_install(
    const struct open_cfw_em9305_qpc_port_providers *providers);
void open_cfw_em9305_qpc_port_reset(void);
uint32_t open_cfw_em9305_qpc_port_is_configured(void);
enum open_cfw_em9305_qpc_port_fault
open_cfw_em9305_qpc_port_last_fault(void);

#ifdef __cplusplus
}
#endif

#endif
