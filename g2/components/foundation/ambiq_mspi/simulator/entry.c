/* SPDX-License-Identifier: MIT */
#include "../ambiq_mspi_interrupts.h"
/* Callable module only: no vectors, clocks, DMA, IRQ handler or device startup. */
uint32_t ambiq_sim_enable(void *h,uint32_t m){return am_hal_mspi_interrupt_enable(h,m);}
uint32_t ambiq_sim_disable(void *h,uint32_t m){return am_hal_mspi_interrupt_disable(h,m);}
uint32_t ambiq_sim_status(void *h,uint32_t *s,bool only){return am_hal_mspi_interrupt_status_get(h,s,only);}
uint32_t ambiq_sim_clear(void *h,uint32_t m){return am_hal_mspi_interrupt_clear(h,m);}

uint32_t ambiq_sim_controller_disable(void *h){return am_hal_mspi_disable(h);}
uint32_t ambiq_sim_deinitialize(void *h){return am_hal_mspi_deinitialize(h);}
