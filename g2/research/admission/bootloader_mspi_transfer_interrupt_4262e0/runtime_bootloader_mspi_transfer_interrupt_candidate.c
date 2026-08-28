/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_transfer_interrupt_candidate.h"
#if defined(__arm__) || defined(__thumb__)
#include "../../../components/bootloader/core_overlay/runtime_mspi_transfer_interrupt_4262e0.c"
#else
static uint32_t valid(open_cfw_transfer_state*s){return s!=0&&(s->prefix&0x01ffffffU)==0x01bebebeU;}
uint32_t open_cfw_bootloader_mspi_blocking_transfer_4262e0(open_cfw_transfer_state*s,const open_cfw_transfer_request*r,uint32_t timeout,open_cfw_transfer_trace*t){uint32_t status;(void)timeout;if(!valid(s))return 2U;if((s->device==10U||s->device==11U)&&(r->device_address&3U))return 7U;if(r->continue_transfer||s->num_cq||s->num_hp||s->sequence==2U)return 7U;t->saved_inten=s->inten;s->inten=0;t->intclr_writes++;if(r->direction==0U)t->fifo_read_calls++;else if(r->direction==1U)t->fifo_write_calls++;status=t->fifo_status;if(status){t->intclr_writes++;s->inten=t->saved_inten;t->restored_inten=s->inten;return status;}t->status_check_calls++;status=t->status_status;t->intclr_writes++;s->inten=t->saved_inten;t->restored_inten=s->inten;return status;}
uint32_t open_cfw_bootloader_mspi_interrupt_enable_426450(open_cfw_transfer_state*s,uint32_t mask){if(!valid(s))return 2U;s->inten|=mask;return 0U;}
uint32_t open_cfw_bootloader_mspi_interrupt_disable_426484(open_cfw_transfer_state*s,uint32_t mask){if(!valid(s))return 2U;s->inten&=~mask;return 0U;}
uint32_t open_cfw_bootloader_mspi_interrupt_status_get_4264ba(open_cfw_transfer_state*s,uint32_t*out,uint32_t enabled_only){if(!valid(s))return 2U;*out=enabled_only?(s->intstat&s->inten):s->intstat;return 0U;}
#endif
