/* SPDX-License-Identifier: MIT */
/*
 * EM9305 QP/C 6.5.1 target port composition layer.
 *
 * This file deliberately contains no interrupt-controller, radio, UART,
 * voltage-monitor, or MMIO implementation.  Those operations are supplied by
 * an authorized board port.  Missing required providers enter a fail-closed
 * trap and can never be mistaken for successful critical-section handling.
 */

#include "runtime_qpc_port.h"

#include "qf_port.h"

static struct open_cfw_em9305_qpc_port_providers qpc_port;
static uint32_t qpc_port_configured;
static volatile enum open_cfw_em9305_qpc_port_fault qpc_port_fault;

/* QF_init() expects these optional QP/C subsystems even when configured off. */
QSubscrList *QF_subscrList_;
enum_t QF_maxPubSignal_;
QTimeEvt QF_timeEvtHead_[QF_MAX_TICK_RATE];

static void open_cfw_em9305_qpc_port_trap(
    enum open_cfw_em9305_qpc_port_fault fault,
    const char *module,
    int32_t location)
{
    qpc_port_fault = fault;
    if (qpc_port.assertion != 0) {
        qpc_port.assertion(qpc_port.context, module, location);
    }
    for (;;) {
        /* Fail closed.  A reviewed board assertion callback may reset first. */
    }
}

static uint32_t open_cfw_em9305_qpc_port_table_complete(
    const struct open_cfw_em9305_qpc_port_providers *providers)
{
    return (uint32_t)(
        providers != 0 &&
        providers->critical_entry != 0 &&
        providers->critical_exit != 0 &&
        providers->interrupt_disable != 0 &&
        providers->interrupt_enable != 0 &&
        providers->isr_context != 0 &&
        providers->startup != 0 &&
        providers->idle != 0 &&
        providers->assertion != 0);
}

int32_t open_cfw_em9305_qpc_port_install(
    const struct open_cfw_em9305_qpc_port_providers *providers)
{
    if (open_cfw_em9305_qpc_port_table_complete(providers) == 0U) {
        return -1;
    }
    qpc_port.context = providers->context;
    qpc_port.critical_entry = providers->critical_entry;
    qpc_port.critical_exit = providers->critical_exit;
    qpc_port.interrupt_disable = providers->interrupt_disable;
    qpc_port.interrupt_enable = providers->interrupt_enable;
    qpc_port.isr_context = providers->isr_context;
    qpc_port.startup = providers->startup;
    qpc_port.cleanup = providers->cleanup;
    qpc_port.idle = providers->idle;
    qpc_port.assertion = providers->assertion;
    qpc_port_fault = OPEN_CFW_EM9305_QPC_PORT_FAULT_NONE;
    qpc_port_configured = 1U;
    return 0;
}

void open_cfw_em9305_qpc_port_reset(void)
{
    qpc_port.context = 0;
    qpc_port.critical_entry = 0;
    qpc_port.critical_exit = 0;
    qpc_port.interrupt_disable = 0;
    qpc_port.interrupt_enable = 0;
    qpc_port.isr_context = 0;
    qpc_port.startup = 0;
    qpc_port.cleanup = 0;
    qpc_port.idle = 0;
    qpc_port.assertion = 0;
    qpc_port_fault = OPEN_CFW_EM9305_QPC_PORT_FAULT_NONE;
    qpc_port_configured = 0U;
}

uint32_t open_cfw_em9305_qpc_port_is_configured(void)
{
    return qpc_port_configured;
}

enum open_cfw_em9305_qpc_port_fault
open_cfw_em9305_qpc_port_last_fault(void)
{
    return qpc_port_fault;
}

static void open_cfw_em9305_qpc_port_require_configuration(void)
{
    if (qpc_port_configured == 0U) {
        open_cfw_em9305_qpc_port_trap(
            OPEN_CFW_EM9305_QPC_PORT_FAULT_NOT_CONFIGURED,
            "em9305_qpc_port",
            1);
    }
}

QF_CRIT_STAT_TYPE open_cfw_em9305_qf_crit_entry(void)
{
    open_cfw_em9305_qpc_port_require_configuration();
    return qpc_port.critical_entry(qpc_port.context);
}

void open_cfw_em9305_qf_crit_exit(QF_CRIT_STAT_TYPE status)
{
    open_cfw_em9305_qpc_port_require_configuration();
    qpc_port.critical_exit(qpc_port.context, status);
}

void open_cfw_em9305_qf_int_disable(void)
{
    open_cfw_em9305_qpc_port_require_configuration();
    qpc_port.interrupt_disable(qpc_port.context);
}

void open_cfw_em9305_qf_int_enable(void)
{
    open_cfw_em9305_qpc_port_require_configuration();
    qpc_port.interrupt_enable(qpc_port.context);
}

uint_fast8_t open_cfw_em9305_qk_isr_context(void)
{
    open_cfw_em9305_qpc_port_require_configuration();
    return (uint_fast8_t)(qpc_port.isr_context(qpc_port.context) != 0U);
}

void QF_onStartup(void)
{
    open_cfw_em9305_qpc_port_require_configuration();
    qpc_port.startup(qpc_port.context);
}

void QF_onCleanup(void)
{
    open_cfw_em9305_qpc_port_require_configuration();
    if (qpc_port.cleanup != 0) {
        qpc_port.cleanup(qpc_port.context);
    }
}

void QK_onIdle(void)
{
    open_cfw_em9305_qpc_port_require_configuration();
    qpc_port.idle(qpc_port.context);
}

void Q_onAssert(char_t const * const module, int_t location)
{
    open_cfw_em9305_qpc_port_trap(
        OPEN_CFW_EM9305_QPC_PORT_FAULT_QP_ASSERT,
        module,
        (int32_t)location);
}

/* QF_MAX_TICK_RATE is zero for the authenticated controller application. */
void QF_tickX_(uint_fast8_t const tick_rate)
{
    (void)tick_rate;
    open_cfw_em9305_qpc_port_trap(
        OPEN_CFW_EM9305_QPC_PORT_FAULT_UNSUPPORTED_TICK,
        "em9305_qpc_port",
        2);
}
