/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_lifecycle_candidate.h"
#if defined(__arm__) || defined(__thumb__)
#include "../../../components/bootloader/core_overlay/runtime_mspi_lifecycle_425066.c"
#else
static uint32_t valid(open_cfw_mspi_lifecycle_state*s){return s!=0&&(s->prefix&0x01ffffffU)==0x01bebebeU;}
uint32_t open_cfw_bootloader_mspi_enable_425066(open_cfw_mspi_lifecycle_state*s,open_cfw_mspi_lifecycle_trace*t){if(!valid(s))return 2U;if(!s->configured)return 7U;if(s->tcb_address){s->last_processed=0;s->num_cq_entries=0;t->cq_init_calls++;t->cq_setclear=0x00400080U;s->pending_hp_transactions=0;s->hp=0;s->num_hp_pending=0;s->block=0;s->num_hp_entries=0;s->sequence=0;s->num_transactions=0;s->autonomous=1;s->num_unsolicited=0;}s->prefix|=0x02000000U;return 0U;}
uint32_t open_cfw_bootloader_mspi_disable_4250f0(open_cfw_mspi_lifecycle_state*s,open_cfw_mspi_lifecycle_trace*t){if(!valid(s))return 2U;if((s->prefix&0x02000000U)==0U)return 0U;if(s->num_hp_entries||s->num_cq_entries)return 3U;if(s->tcb_address){t->cq_disable_calls++;if(t->cq_disable_status)return t->cq_disable_status;t->cq_term_calls++;}s->prefix&=~0x02000000U;if(s->xip_enabled){t->delay_calls++;t->delay_value=s->xip_delay;}return 0U;}
uint32_t open_cfw_bootloader_mspi_deinitialize_42516c(open_cfw_mspi_lifecycle_state*s,open_cfw_mspi_lifecycle_trace*t){if(!valid(s))return 2U;if(s->prefix&0x02000000U)(void)open_cfw_bootloader_mspi_disable_4250f0(s,t);s->prefix&=~0x01000000U;s->module=0U;return 0U;}
#endif
