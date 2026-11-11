/* Native QF_init 0x311014..0x31105e and QF_bzero 0x310fac..0x310fb8.
 * The QP/C 6.5.1 globals live at their stock SRAM addresses (pins in link/g2-em9305.ld, declared in
 * qpc-port/qp_unit.h); QF_subscrList_ (0x801390) and QF_maxPubSignal_ (0x801364) are defined here because
 * the stock image has no qf_ps.c, only QF_init's zeroing stores.
 */
#include <stdint.h>
#include "qp_unit.h"
#include "qf_pkg.h"

QSubscrList *QF_subscrList_;
enum_t QF_maxPubSignal_;

extern void *opencfw_em9305_memset(void *destination,uint32_t value,uint32_t bytes); /* 0x33301c */
void QF_bzero(void * const start,uint_fast16_t len)
{
    if (len != 0U) (void)opencfw_em9305_memset(start,0,len);
}
void QF_init(void)
{
    QF_subscrList_ = (QSubscrList *)0;
    QF_maxPool_ = 0U;
    QF_maxPubSignal_ = (enum_t)0;
    QF_bzero(&QK_attr_,0U);
    QF_bzero(QF_active_,(uint_fast16_t)sizeof(QF_active_));
    QF_bzero(&QK_attr_,(uint_fast16_t)sizeof(QK_attr_));
    QK_attr_.actPrio = 0U;
    QK_attr_.lockPrio = (uint8_t)QF_MAX_ACTIVE; /* scheduler locked until QK_onStartup / QF_run */
}
