/* SPDX-License-Identifier: BSD-3-Clause */
#ifndef OPEN_CFW_BOOTLOADER_RUNTIME_MSPI_LIFECYCLE_425066_H
#define OPEN_CFW_BOOTLOADER_RUNTIME_MSPI_LIFECYCLE_425066_H

typedef __UINT8_TYPE__ open_cfw_mspi_lifecycle_u8;
typedef __UINT32_TYPE__ open_cfw_mspi_lifecycle_u32;

#if defined(__arm__) || defined(__thumb__)
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_enable_425066(void *handle);
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_disable_4250f0(void *handle);
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_deinitialize_42516c(void *handle);
#else
typedef struct open_cfw_mspi_lifecycle_state {
    open_cfw_mspi_lifecycle_u32 prefix, module, tcb_size, tcb_address;
    open_cfw_mspi_lifecycle_u32 last_processed, num_cq_entries;
    open_cfw_mspi_lifecycle_u32 num_hp_entries, num_hp_pending, block;
    open_cfw_mspi_lifecycle_u32 num_transactions, pending_hp_transactions;
    open_cfw_mspi_lifecycle_u32 num_unsolicited, xip_delay;
    open_cfw_mspi_lifecycle_u8 configured, hp, sequence, autonomous, xip_enabled;
} open_cfw_mspi_lifecycle_state;
typedef struct open_cfw_mspi_lifecycle_trace {
    open_cfw_mspi_lifecycle_u32 cq_init_calls, cq_disable_calls, cq_term_calls;
    open_cfw_mspi_lifecycle_u32 delay_calls, delay_value, cq_setclear;
    open_cfw_mspi_lifecycle_u32 cq_disable_status;
} open_cfw_mspi_lifecycle_trace;
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_enable_425066(
    open_cfw_mspi_lifecycle_state *state, open_cfw_mspi_lifecycle_trace *trace);
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_disable_4250f0(
    open_cfw_mspi_lifecycle_state *state, open_cfw_mspi_lifecycle_trace *trace);
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_deinitialize_42516c(
    open_cfw_mspi_lifecycle_state *state, open_cfw_mspi_lifecycle_trace *trace);
#endif
#endif
