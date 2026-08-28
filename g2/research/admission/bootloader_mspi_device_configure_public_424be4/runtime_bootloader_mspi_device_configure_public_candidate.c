/* SPDX-License-Identifier: BSD-3-Clause */
#include "runtime_bootloader_mspi_device_configure_public_candidate.h"
#if defined(__arm__) || defined(__thumb__)
#include "../../../components/bootloader/core_overlay/runtime_mspi_device_configure_public_424be4.c"
#else
static uint8_t is_hfrc2(uint8_t f){return f==23U||f==21U||f==19U||f==17U||f==15U||f==13U||f==11U||f==9U||f==7U||f==5U||f==3U;}
static uint8_t delay_for(uint8_t f,uint8_t old){if(f>=6U&&f<=9U)return 8U;if(f>=10U&&f<=13U)return 4U;if((f>=14U&&f<=15U)||(f>=18U&&f<=19U))return 2U;if(f>=20U&&f<=23U)return 1U;return old;}
uint32_t open_cfw_bootloader_mspi_device_configure_public_424be4(open_cfw_mspi_public_state *s,const open_cfw_mspi_public_config *c,open_cfw_mspi_public_trace *t){uint8_t source,sel,div;
 if(s==0||(s->prefix&0x01ffffffU)!=0x01bebebeU)return 2U;if(!s->configured)return 7U;
 if((s->module==1U||s->module==2U)&&(((c->frequency>=21U)&&(c->frequency<=23U))||(c->device==10U||c->device==11U)))return 5U;
 t->clock_calls++;t->clock_disable_module=s->module;
 source=is_hfrc2(c->frequency)?5U:4U;
 if(s->clock_source!=source){t->release_calls++;t->released_source=s->clock_source;if(t->release_status)return t->release_status;t->request_calls++;t->requested_source=source;if(t->request_status)return t->request_status;}s->clock_source=source;
 if(c->frequency<1U||c->frequency>23U)return 5U;
 sel=is_hfrc2(c->frequency)?10U:(c->frequency==1U?7U:8U);t->clock_calls++;t->clock_enable_module=s->module;t->clock_select=sel;
 if(c->frequency>=20U)div=1U;else if(c->frequency>=18U)div=2U;else if(c->frequency>=16U)div=3U;else if(c->frequency>=14U)div=4U;else if(c->frequency>=12U)div=6U;else if(c->frequency>=10U)div=8U;else if(c->frequency>=8U)div=12U;else if(c->frequency>=6U)div=16U;else if(c->frequency>=4U)div=24U;else div=32U;
 t->divisor=div;t->sdr250=(c->frequency==22U||c->frequency==23U);if(s->tcb_address)t->high_speed_thresholds=(c->frequency>=18U);s->device=c->device;t->device_config_calls++;s->big_endian=0U;s->clock_frequency=c->frequency;s->wait_timeout=10000U;s->xip_delay=delay_for(c->frequency,s->xip_delay);return 0U;}
#endif
