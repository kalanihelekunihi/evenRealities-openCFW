/* SPDX-License-Identifier: MIT */
/* Clean-room reconstruction of three bounded G2 bootloader IRQ services. */

typedef __INT16_TYPE__ open_cfw_irq_i16;
typedef __UINT8_TYPE__ open_cfw_irq_u8;
typedef __UINT16_TYPE__ open_cfw_irq_u16;
typedef __UINT32_TYPE__ open_cfw_irq_u32;
typedef __UINTPTR_TYPE__ open_cfw_irq_uintptr;

enum {
    OPEN_CFW_NVIC_ISER = 0xE000E100U,
    OPEN_CFW_NVIC_IPR = 0xE000E400U,
    OPEN_CFW_SCB_SHP = 0xE000ED18U,
    OPEN_CFW_MSPI_HANDLE_WORD = 0x200270DCU,
    OPEN_CFW_MSPI_STATUS_GET_THUMB = 0x004264BBU,
    OPEN_CFW_MSPI_CLEAR_THUMB = 0x00426507U,
    OPEN_CFW_MSPI_SERVICE_THUMB = 0x00426537U
};

typedef open_cfw_irq_u32 (*open_cfw_mspi_status_fn)(
    void *, open_cfw_irq_u32 *, open_cfw_irq_u32);
typedef open_cfw_irq_u32 (*open_cfw_mspi_mask_fn)(void *, open_cfw_irq_u32);

#if defined(OPEN_CFW_IRQ_SERVICES_HOST)
void open_cfw_irq_host_enable(open_cfw_irq_u32, open_cfw_irq_u32);
void open_cfw_irq_host_priority(open_cfw_irq_u32, open_cfw_irq_u8);
void open_cfw_irq_host_system_priority(open_cfw_irq_u32, open_cfw_irq_u8);
void *open_cfw_irq_host_mspi_handle(void);
void open_cfw_irq_host_mspi_status(void *, open_cfw_irq_u32 *, open_cfw_irq_u32);
void open_cfw_irq_host_mspi_clear(void *, open_cfw_irq_u32);
void open_cfw_irq_host_mspi_service(void *, open_cfw_irq_u32);
#endif

__attribute__((used, noinline))
void open_cfw_bootloader_nvic_enable_irq_41fdc0(open_cfw_irq_u32 interrupt)
{
    open_cfw_irq_i16 irq = (open_cfw_irq_i16)interrupt;
    open_cfw_irq_u32 index;
    open_cfw_irq_u32 mask;
    if (irq < 0) {
        return;
    }
    index = ((open_cfw_irq_u16)irq) >> 5;
    mask = 1U << (((open_cfw_irq_u32)interrupt) & 31U);
#if defined(OPEN_CFW_IRQ_SERVICES_HOST)
    open_cfw_irq_host_enable(index, mask);
#else
    ((volatile open_cfw_irq_u32 *)(open_cfw_irq_uintptr)OPEN_CFW_NVIC_ISER)[index] = mask;
#endif
}

__attribute__((used, noinline))
void open_cfw_bootloader_nvic_set_priority_41fdde(
    open_cfw_irq_u32 interrupt,
    open_cfw_irq_u32 priority)
{
    open_cfw_irq_i16 irq = (open_cfw_irq_i16)interrupt;
    open_cfw_irq_u8 encoded = (open_cfw_irq_u8)(priority << 4);
    if (irq >= 0) {
#if defined(OPEN_CFW_IRQ_SERVICES_HOST)
        open_cfw_irq_host_priority((open_cfw_irq_u16)irq, encoded);
#else
        ((volatile open_cfw_irq_u8 *)(open_cfw_irq_uintptr)OPEN_CFW_NVIC_IPR)[
            (open_cfw_irq_u16)irq] = encoded;
#endif
    } else {
        open_cfw_irq_u32 index = ((open_cfw_irq_u16)irq & 15U) - 4U;
#if defined(OPEN_CFW_IRQ_SERVICES_HOST)
        open_cfw_irq_host_system_priority(index, encoded);
#else
        ((volatile open_cfw_irq_u8 *)(open_cfw_irq_uintptr)OPEN_CFW_SCB_SHP)[index] = encoded;
#endif
    }
}

__attribute__((used, noinline))
void open_cfw_bootloader_mspi_isr_41fe06(void)
{
    void *handle;
    open_cfw_irq_u32 status;
#if defined(OPEN_CFW_IRQ_SERVICES_HOST)
    handle = open_cfw_irq_host_mspi_handle();
    open_cfw_irq_host_mspi_status(handle, &status, 0U);
    open_cfw_irq_host_mspi_clear(handle, status);
    open_cfw_irq_host_mspi_service(handle, status);
#else
    handle = *(void **)(open_cfw_irq_uintptr)OPEN_CFW_MSPI_HANDLE_WORD;
    (void)((open_cfw_mspi_status_fn)(open_cfw_irq_uintptr)
        OPEN_CFW_MSPI_STATUS_GET_THUMB)(handle, &status, 0U);
    (void)((open_cfw_mspi_mask_fn)(open_cfw_irq_uintptr)
        OPEN_CFW_MSPI_CLEAR_THUMB)(handle, status);
    (void)((open_cfw_mspi_mask_fn)(open_cfw_irq_uintptr)
        OPEN_CFW_MSPI_SERVICE_THUMB)(handle, status);
#endif
}
