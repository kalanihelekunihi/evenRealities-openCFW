/* SPDX-License-Identifier: BSD-3-Clause */
/* Structured AmbiqSuite-compatible G2 public MSPI device configuration. */

#include "runtime_mspi_device_configure_public_424be4.h"

_Static_assert(__builtin_offsetof(open_cfw_mspi_public_config, read_instruction) == 4U,
               "G2 read-instruction ABI offset changed");
_Static_assert(__builtin_offsetof(open_cfw_mspi_public_config, dma_time_limit) == 20U,
               "G2 DMA time-limit ABI offset changed");
_Static_assert(__builtin_offsetof(open_cfw_mspi_public_config, dma_boundary) == 22U,
               "G2 DMA-boundary ABI offset changed");

static __attribute__((always_inline)) inline open_cfw_mspi_public_u32
load32(const volatile open_cfw_mspi_public_u8 *pointer)
{
    return *(const volatile open_cfw_mspi_public_u32 *)(const volatile void *)pointer;
}

static __attribute__((always_inline)) inline void store32(
    volatile open_cfw_mspi_public_u8 *pointer, open_cfw_mspi_public_u32 value)
{
    *(volatile open_cfw_mspi_public_u32 *)(volatile void *)pointer = value;
}

static __attribute__((always_inline)) inline open_cfw_mspi_public_u8
is_hfrc2(open_cfw_mspi_public_u8 frequency)
{
    return (frequency >= 3U && frequency <= 23U &&
            (frequency & 1U) != 0U) ? 1U : 0U;
}

static __attribute__((always_inline)) inline open_cfw_mspi_public_u8
clock_divisor(open_cfw_mspi_public_u8 frequency)
{
    if (frequency >= 20U) return 1U;
    if (frequency >= 18U) return 2U;
    if (frequency >= 16U) return 3U;
    if (frequency >= 14U) return 4U;
    if (frequency >= 12U) return 6U;
    if (frequency >= 10U) return 8U;
    if (frequency >= 8U) return 12U;
    if (frequency >= 6U) return 16U;
    if (frequency >= 4U) return 24U;
    return 32U;
}

#if defined(__arm__) || defined(__thumb__)
extern void open_cfw_bootloader_mspi_clkgen_ctrl_4249a0(
    open_cfw_mspi_public_u32, open_cfw_mspi_public_u32,
    open_cfw_mspi_public_u32, open_cfw_mspi_public_u32);
extern open_cfw_mspi_public_u32 open_cfw_bootloader_clock_release_422364(
    open_cfw_mspi_public_u32, open_cfw_mspi_public_u32);
extern open_cfw_mspi_public_u32 open_cfw_bootloader_clock_request_4222f0(
    open_cfw_mspi_public_u32, open_cfw_mspi_public_u32);
extern open_cfw_mspi_public_u32 open_cfw_bootloader_mspi_device_configure_424120(
    const void *);
extern void open_cfw_bootloader_mspi_xip_off_delay_424a18(void *);

__attribute__((aligned(2)))
open_cfw_mspi_public_u32
open_cfw_bootloader_mspi_device_configure_public_424be4(
    void *handle, const open_cfw_mspi_public_config *configuration)
{
    volatile open_cfw_mspi_public_u8 *state;
    volatile open_cfw_mspi_public_u8 *registers;
    open_cfw_mspi_public_u32 prefix, module, source, status, value;
    open_cfw_mspi_public_u8 frequency, divisor, selector;

    if (handle == (void *)0) return 2U;
    state = (volatile open_cfw_mspi_public_u8 *)handle;
    prefix = load32(state);
    if ((prefix & 0x01FFFFFFU) != 0x01BEBEBEU) return 2U;
    if (state[8U] == 0U) return 7U;
    module = load32(state + 4U);
    frequency = configuration->frequency;
    if ((module == 1U || module == 2U) &&
        ((frequency >= 21U && frequency <= 23U) ||
         configuration->device == 10U || configuration->device == 11U))
        return 5U;
    open_cfw_bootloader_mspi_clkgen_ctrl_4249a0(module, 0U, 0U, 0U);
    source = is_hfrc2(frequency) != 0U ? 5U : 4U;
    if (state[0x8C9U] != source) {
        status = open_cfw_bootloader_clock_release_422364(
            state[0x8C9U], (module + 0x10U) & 0xFFU);
        if (status != 0U) return status;
        status = open_cfw_bootloader_clock_request_4222f0(
            source, (module + 0x10U) & 0xFFU);
        if (status != 0U) return status;
    }
    state[0x8C9U] = (open_cfw_mspi_public_u8)source;
    if (frequency < 1U || frequency > 23U) return 5U;
    selector = source == 5U ? 10U : frequency == 1U ? 7U : 8U;
    open_cfw_bootloader_mspi_clkgen_ctrl_4249a0(module, 1U, 1U, selector);
    registers = (volatile open_cfw_mspi_public_u8 *)(__UINTPTR_TYPE__)(
        0x40060000U + module * 0x1000U);
    value = load32(registers + 0x8CU);
    value = (frequency == 22U || frequency == 23U)
        ? value | 0x40000000U : value & ~0x40000000U;
    store32(registers + 0x8CU, value);

    divisor = clock_divisor(frequency);
    value = ((open_cfw_mspi_public_u32)configuration->address_size << 5U) |
            ((open_cfw_mspi_public_u32)configuration->instruction_size << 7U) |
            ((open_cfw_mspi_public_u32)configuration->turnaround << 8U) |
            ((open_cfw_mspi_public_u32)divisor << 16U) |
            ((open_cfw_mspi_public_u32)configuration->write_latency << 26U);
    value |= ((open_cfw_mspi_public_u32)(configuration->spi_mode & 1U) << 15U) |
             ((open_cfw_mspi_public_u32)(configuration->spi_mode >> 1U) << 14U);
    if (frequency >= 20U) value |= 0x01000000U;
    store32(registers + 0x84U, value);
    value = load32(registers + 0x88U);
    value = (value & ~1U) | (configuration->emulate_ddr != 0U ? 1U : 0U);
    store32(registers + 0x88U, value);
    value = load32(registers + 0x8CU);
    value = (value & ~(3U << 17U)) |
            ((open_cfw_mspi_public_u32)(configuration->ce_latency & 3U) << 17U);
    store32(registers + 0x8CU, value);
    store32(registers + 0x30U,
            (load32(registers + 0x30U) & ~0xF1U) | 0x70U);

    value = load32(registers + 0x90U) & ~0x03FFE0FCU;
    value |= 0xCU | ((open_cfw_mspi_public_u32)state[13U] << 4U);
    if (configuration->enable_turnaround != 0U)
        value |= 0x20U |
                 ((open_cfw_mspi_public_u32)configuration->turnaround << 14U);
    if (configuration->send_address != 0U) value |= 0x40U;
    if (configuration->send_instruction != 0U) value |= 0x80U;
    value |= ((open_cfw_mspi_public_u32)configuration->enable_write_latency << 13U) |
             ((open_cfw_mspi_public_u32)configuration->write_latency << 20U);
    store32(registers + 0x90U, value);
    store32(registers + 0x94U,
            configuration->write_instruction |
            ((open_cfw_mspi_public_u32)configuration->read_instruction << 16U));
    store32(registers + 0x98U,
            (configuration->dma_time_limit & 0x0FFFU) |
            ((open_cfw_mspi_public_u32)(configuration->dma_boundary & 0xFU) << 12U));

    state[13U] = 0U;
    if (load32(state + 0x18U) != 0U) {
        store32(registers + 0x114U, 32U);
        value = frequency >= 18U ? 12U : 8U;
        store32(registers + 0x118U, value | (8U << 8U));
        store32(registers + 0x20U,
                (load32(registers + 0x20U) & ~(0x3FU << 8U)) | (30U << 8U));
    }
    state[10U] = configuration->device;
    (void)open_cfw_bootloader_mspi_device_configure_424120((const void *)state);
    state[13U] = 0U;
    state[12U] = frequency;
    store32(state + 0x10U, 10000U);
    open_cfw_bootloader_mspi_xip_off_delay_424a18((void *)state);
    return 0U;
}
#else
open_cfw_mspi_public_u32
open_cfw_bootloader_mspi_device_configure_public_424be4(
    open_cfw_mspi_public_u8 *state,
    const open_cfw_mspi_public_config *configuration,
    open_cfw_mspi_public_trace *trace)
{
    open_cfw_mspi_public_u8 frequency, source, selector, divisor;
    open_cfw_mspi_public_u32 module;
    if (state == (open_cfw_mspi_public_u8 *)0 ||
        (load32(state) & 0x01FFFFFFU) != 0x01BEBEBEU) return 2U;
    if (state[8U] == 0U) return 7U;
    module = load32(state + 4U);
    frequency = configuration->frequency;
    if ((module == 1U || module == 2U) &&
        ((frequency >= 21U && frequency <= 23U) ||
         configuration->device == 10U || configuration->device == 11U))
        return 5U;
    trace->clock_calls++; trace->clock_disable_module = module;
    source = is_hfrc2(frequency) != 0U ? 5U : 4U;
    if (state[0x8C9U] != source) {
        trace->release_calls++; trace->released_source = state[0x8C9U];
        if (trace->release_status != 0U) return trace->release_status;
        trace->request_calls++; trace->requested_source = source;
        if (trace->request_status != 0U) return trace->request_status;
    }
    state[0x8C9U] = source;
    if (frequency < 1U || frequency > 23U) return 5U;
    selector = source == 5U ? 10U : frequency == 1U ? 7U : 8U;
    trace->clock_calls++; trace->clock_enable_module = module;
    trace->clock_select = selector;
    divisor = clock_divisor(frequency); trace->divisor = divisor;
    trace->sdr250 = frequency == 22U || frequency == 23U;
    if (load32(state + 0x18U) != 0U)
        trace->high_speed_thresholds = frequency >= 18U;
    state[10U] = configuration->device; trace->device_config_calls++;
    state[13U] = 0U; state[12U] = frequency;
    store32(state + 0x10U, 10000U);
    if (frequency >= 6U && frequency <= 9U) store32(state + 0x8CCU, 8U);
    else if (frequency >= 10U && frequency <= 13U) store32(state + 0x8CCU, 4U);
    else if ((frequency >= 14U && frequency <= 15U) ||
             (frequency >= 18U && frequency <= 19U)) store32(state + 0x8CCU, 2U);
    else if (frequency >= 20U) store32(state + 0x8CCU, 1U);
    return 0U;
}
#endif
