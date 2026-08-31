/* SPDX-License-Identifier: BSD-3-Clause */
/* Structured AmbiqSuite-compatible G2 MSPI lifecycle services. */
#include "runtime_mspi_lifecycle_425066.h"

static __attribute__((always_inline)) inline open_cfw_mspi_lifecycle_u32
load32(const volatile open_cfw_mspi_lifecycle_u8 *pointer)
{
    return *(const volatile open_cfw_mspi_lifecycle_u32 *)(const volatile void *)pointer;
}
static __attribute__((always_inline)) inline void store32(
    volatile open_cfw_mspi_lifecycle_u8 *pointer,
    open_cfw_mspi_lifecycle_u32 value)
{
    *(volatile open_cfw_mspi_lifecycle_u32 *)(volatile void *)pointer = value;
}
static __attribute__((always_inline)) inline open_cfw_mspi_lifecycle_u8
valid_prefix(open_cfw_mspi_lifecycle_u32 prefix)
{
    return (prefix & 0x01FFFFFFU) == 0x01BEBEBEU;
}

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_mspi_cq_init_423f28(
    open_cfw_mspi_lifecycle_u32 module, open_cfw_mspi_lifecycle_u32 size,
    const void *buffer);
extern open_cfw_mspi_lifecycle_u32
open_cfw_bootloader_mspi_cq_disable_423fac(void *handle);
extern open_cfw_mspi_lifecycle_u32
open_cfw_bootloader_mspi_cq_term_423f54(void *handle);
extern void open_cfw_bootloader_delay_us_41d1c0(open_cfw_mspi_lifecycle_u32 delay);

__attribute__((aligned(2)))
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_enable_425066(void *handle)
{
    volatile open_cfw_mspi_lifecycle_u8 *state;
    volatile open_cfw_mspi_lifecycle_u8 *registers;
    open_cfw_mspi_lifecycle_u32 prefix, module;
    if (handle == (void *)0) return 2U;
    state = (volatile open_cfw_mspi_lifecycle_u8 *)handle;
    prefix = load32(state);
    if (!valid_prefix(prefix)) return 2U;
    if (state[8U] == 0U) return 7U;
    if (load32(state + 0x18U) != 0U) {
        store32(state + 0x1CU, 0U);
        store32(state + 0x20U, 0U);
        module = load32(state + 4U);
        open_cfw_bootloader_mspi_cq_init_423f28(
            module, load32(state + 0x14U),
            (const void *)(__UINTPTR_TYPE__)load32(state + 0x18U));
        registers = (volatile open_cfw_mspi_lifecycle_u8 *)(__UINTPTR_TYPE__)(
            0x40060000U + module * 0x1000U);
        store32(registers + 0x2B4U, 0x00400080U);
        store32(state + 0x854U, 0U);
        state[0x83CU] = 0U;
        store32(state + 0x844U, 0U);
        store32(state + 0x838U, 0U);
        store32(state + 0x840U, 0U);
        state[0x82CU] = 0U;
        store32(state + 0x830U, 0U);
        state[0x82DU] = 1U;
        store32(state + 0x85CU, 0U);
    }
    store32(state, prefix | 0x02000000U);
    return 0U;
}

__attribute__((aligned(2)))
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_disable_4250f0(void *handle)
{
    volatile open_cfw_mspi_lifecycle_u8 *state;
    volatile open_cfw_mspi_lifecycle_u8 *registers;
    open_cfw_mspi_lifecycle_u32 prefix, status, module;
    if (handle == (void *)0) return 2U;
    state = (volatile open_cfw_mspi_lifecycle_u8 *)handle;
    prefix = load32(state);
    if (!valid_prefix(prefix)) return 2U;
    if ((prefix & 0x02000000U) == 0U) return 0U;
    if (load32(state + 0x840U) != 0U || load32(state + 0x20U) != 0U)
        return 3U;
    if (load32(state + 0x18U) != 0U) {
        status = open_cfw_bootloader_mspi_cq_disable_423fac(handle);
        if (status != 0U) return status;
        (void)open_cfw_bootloader_mspi_cq_term_423f54(handle);
    }
    store32(state, prefix & ~0x02000000U);
    module = load32(state + 4U);
    registers = (volatile open_cfw_mspi_lifecycle_u8 *)(__UINTPTR_TYPE__)(
        0x40060000U + module * 0x1000U);
    if ((load32(registers + 0x90U) & 1U) != 0U)
        open_cfw_bootloader_delay_us_41d1c0(load32(state + 0x8CCU));
    return 0U;
}

__attribute__((aligned(2)))
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_deinitialize_42516c(void *handle)
{
    volatile open_cfw_mspi_lifecycle_u8 *state;
    open_cfw_mspi_lifecycle_u32 prefix;
    if (handle == (void *)0) return 2U;
    state = (volatile open_cfw_mspi_lifecycle_u8 *)handle;
    prefix = load32(state);
    if (!valid_prefix(prefix)) return 2U;
    if ((prefix & 0x02000000U) != 0U)
        (void)open_cfw_bootloader_mspi_disable_4250f0(handle);
    store32(state, load32(state) & ~0x01000000U);
    store32(state + 4U, 0U);
    return 0U;
}
#else
static open_cfw_mspi_lifecycle_u8 valid(open_cfw_mspi_lifecycle_state *state)
{ return state != (void *)0 && valid_prefix(state->prefix); }
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_enable_425066(
    open_cfw_mspi_lifecycle_state *state, open_cfw_mspi_lifecycle_trace *trace)
{
    if (!valid(state)) return 2U; if (!state->configured) return 7U;
    if (state->tcb_address) {
        state->last_processed=0; state->num_cq_entries=0; trace->cq_init_calls++;
        trace->cq_setclear=0x00400080U; state->pending_hp_transactions=0;
        state->hp=0; state->num_hp_pending=0; state->block=0;
        state->num_hp_entries=0; state->sequence=0; state->num_transactions=0;
        state->autonomous=1; state->num_unsolicited=0;
    }
    state->prefix|=0x02000000U; return 0U;
}
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_disable_4250f0(
    open_cfw_mspi_lifecycle_state *state, open_cfw_mspi_lifecycle_trace *trace)
{
    if (!valid(state)) return 2U; if (!(state->prefix&0x02000000U)) return 0U;
    if (state->num_hp_entries||state->num_cq_entries) return 3U;
    if (state->tcb_address) { trace->cq_disable_calls++;
        if (trace->cq_disable_status) return trace->cq_disable_status;
        trace->cq_term_calls++; }
    state->prefix&=~0x02000000U;
    if (state->xip_enabled) { trace->delay_calls++; trace->delay_value=state->xip_delay; }
    return 0U;
}
open_cfw_mspi_lifecycle_u32 open_cfw_bootloader_mspi_deinitialize_42516c(
    open_cfw_mspi_lifecycle_state *state, open_cfw_mspi_lifecycle_trace *trace)
{
    if (!valid(state)) return 2U;
    if (state->prefix&0x02000000U)
        (void)open_cfw_bootloader_mspi_disable_4250f0(state,trace);
    state->prefix&=~0x01000000U; state->module=0U; return 0U;
}
#endif
