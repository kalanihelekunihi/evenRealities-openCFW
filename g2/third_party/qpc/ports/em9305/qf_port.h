/* GPL-3.0-or-later; recovered G2 EM9305 QP/C 6.5.1 ABI configuration. */
#ifndef OPEN_CFW_EM9305_QF_PORT_H
#define OPEN_CFW_EM9305_QF_PORT_H
#include <stdint.h>
#define QF_MAX_ACTIVE 16
#define QF_MAX_EPOOL 2
#define QF_MAX_TICK_RATE 0
#define QF_EVENT_SIZ_SIZE 2
#define QF_EQUEUE_CTR_SIZE 1
#define QF_MPOOL_SIZ_SIZE 2
#define QF_MPOOL_CTR_SIZE 2
#define QF_TIMEEVT_CTR_SIZE 2
#define QF_CRIT_STAT_TYPE uint32_t
QF_CRIT_STAT_TYPE open_cfw_em9305_qf_crit_entry(void);
void open_cfw_em9305_qf_crit_exit(QF_CRIT_STAT_TYPE status);
void open_cfw_em9305_qf_int_disable(void);
void open_cfw_em9305_qf_int_enable(void);
#define QF_CRIT_ENTRY(stat_) ((stat_) = open_cfw_em9305_qf_crit_entry())
#define QF_CRIT_EXIT(stat_) open_cfw_em9305_qf_crit_exit(stat_)
#define QF_INT_DISABLE() open_cfw_em9305_qf_int_disable()
#define QF_INT_ENABLE() open_cfw_em9305_qf_int_enable()
#include "qep_port.h"
#include "qk_port.h"
#include "qf.h"
#endif
