/* Internal NVMC operations arbitrated through Cordio's baseband scheduler. */
#if defined(R1_CORDIO_RTC0)
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "nrf.h"
#include "nrf_error.h"
#include "nrf_sdh.h"
#include "nrf_soc.h"
#include "nrf_fstorage.h"
#include "FreeRTOS.h"
#include "task.h"
#include "bb_api.h"
#include "pal_bb.h"
#include "sch_api.h"
#include "r1_flash_cordio.h"
#include "r1_soc_event_cordio.h"

enum {
    R1_FLASH_PAGE_BYTES = 4096u,
    R1_FLASH_STORAGE_START = 0x000d1000u,
    R1_FLASH_BOOTLOADER_START = 0x000f8000u,
    R1_FLASH_WORDS_PER_SLOT = 4u,
    R1_FLASH_ERASE_STEP_MS = 1u,
    R1_FLASH_ERASE_MIN_STEPS = 90u,
    R1_FLASH_ERASE_MAX_STEPS = 160u,
    R1_FLASH_SLOT_US = 2500u,
};

typedef enum { FLASH_NONE, FLASH_WRITE, FLASH_ERASE } flash_kind_t;
typedef struct {
    flash_kind_t kind;
    uint32_t address;
    const uint32_t *source;
    uint32_t words;
    uint32_t progress;
    uint16_t partial_steps;
    bool scheduled;
    bool finished;
    bool failed;
} flash_operation_t;

static flash_operation_t operation;
static BbOpDesc_t flash_bod;
static bool registered;
static bool baseband_held;
static bool shutdown_waiting;
static uint8_t sync_busy;

static bool storage_layout_valid(void)
{
    const uint32_t page_bytes = *(volatile const uint32_t *)0x10000010u;
    const uint32_t page_count = *(volatile const uint32_t *)0x10000014u;
    const uint32_t bootloader = *(volatile const uint32_t *)0x10001014u;
    return page_bytes == R1_FLASH_PAGE_BYTES && page_count == 256u &&
           bootloader == R1_FLASH_BOOTLOADER_START;
}

static bool in_storage(uint32_t address, uint32_t bytes)
{
    return address >= R1_FLASH_STORAGE_START && bytes != 0u &&
           address < R1_FLASH_BOOTLOADER_START &&
           bytes <= R1_FLASH_BOOTLOADER_START - address;
}

static void nvmc_wait(void)
{
    while (NRF_NVMC->READY == NVMC_READY_READY_Busy) { }
}

static void nvmc_read_mode(void)
{
    NRF_NVMC->CONFIG = NVMC_CONFIG_WEN_Ren;
    __DSB();
    __ISB();
}

static bool erased(uint32_t address)
{
    const volatile uint32_t *words = (const volatile uint32_t *)address;
    for (uint32_t i = 0; i < R1_FLASH_PAGE_BYTES / 4u; ++i)
        if (words[i] != UINT32_MAX) return false;
    return true;
}

static void nvmc_partial_erase(uint32_t address)
{
    NRF_NVMC->CONFIG = NVMC_CONFIG_WEN_Een;
    __DSB();
    __ISB();
    NRF_NVMC->ERASEPAGEPARTIALCFG = R1_FLASH_ERASE_STEP_MS;
    NRF_NVMC->ERASEPAGEPARTIAL = address;
    nvmc_wait();
    nvmc_read_mode();
}

static bool nvmc_full_erase(uint32_t address)
{
    NRF_NVMC->CONFIG = NVMC_CONFIG_WEN_Een;
    __DSB();
    __ISB();
    NRF_NVMC->ERASEPAGE = address;
    nvmc_wait();
    nvmc_read_mode();
    return erased(address);
}

static bool nvmc_write_chunk(uint32_t address, const uint32_t *source,
                             uint32_t words)
{
    volatile uint32_t *target = (volatile uint32_t *)address;
    NRF_NVMC->CONFIG = NVMC_CONFIG_WEN_Wen;
    __DSB();
    __ISB();
    for (uint32_t i = 0; i < words; ++i) {
        target[i] = source[i];
        nvmc_wait();
    }
    nvmc_read_mode();
    for (uint32_t i = 0; i < words; ++i)
        if (target[i] != source[i]) return false;
    return true;
}

static void flash_slot(BbOpDesc_t *bod)
{
    (void)bod;
    if (operation.kind == FLASH_ERASE) {
        nvmc_partial_erase(operation.address);
        ++operation.partial_steps;
        if (operation.partial_steps >= R1_FLASH_ERASE_MIN_STEPS &&
            erased(operation.address))
            operation.finished = true;
        else if (operation.partial_steps >= R1_FLASH_ERASE_MAX_STEPS) {
            operation.failed = true;
            operation.finished = true;
        }
    } else if (operation.kind == FLASH_WRITE) {
        uint32_t remaining = operation.words - operation.progress;
        uint32_t count = remaining < R1_FLASH_WORDS_PER_SLOT ?
                         remaining : R1_FLASH_WORDS_PER_SLOT;
        uint32_t offset = operation.progress;
        if (!nvmc_write_chunk(operation.address + offset * 4u,
                              operation.source + offset, count)) {
            operation.failed = true;
            operation.finished = true;
        } else {
            operation.progress += count;
            operation.finished = operation.progress == operation.words;
        }
    }
    BbTerminateBod();
}

static void flash_slot_end(BbOpDesc_t *bod)
{
    (void)bod;
    operation.scheduled = false;
}

static void flash_slot_abort(BbOpDesc_t *bod)
{
    (void)bod;
    operation.scheduled = false;
}

static void flash_protocol_start(void) { }
static void flash_protocol_stop(void) { }
static void flash_protocol_cancel(BbOpDesc_t *bod) { (void)bod; }

void r1_cordio_flash_register(void)
{
    if (registered) return;
    BbRegisterProt(BB_PROT_NONE, flash_slot, flash_protocol_cancel,
                   flash_protocol_start, flash_protocol_stop);
    registered = true;
}

void r1_cordio_flash_disable(void)
{
    if (baseband_held) {
        BbStop(BB_PROT_NONE);
        baseband_held = false;
    }
    registered = false;
}

bool r1_cordio_flash_busy(void)
{
    return __atomic_load_n(&operation.kind, __ATOMIC_ACQUIRE) != FLASH_NONE ||
           nrf_fstorage_is_busy(NULL);
}

void r1_cordio_flash_wait_for_shutdown(void)
{
    __atomic_store_n(&shutdown_waiting, true, __ATOMIC_RELEASE);
}

void r1_cordio_flash_service(void)
{
    if (!registered) return;
    if (__atomic_load_n(&operation.kind, __ATOMIC_ACQUIRE) == FLASH_NONE) {
        if (__atomic_load_n(&shutdown_waiting, __ATOMIC_ACQUIRE) &&
            !nrf_fstorage_is_busy(NULL)) {
            __atomic_store_n(&shutdown_waiting, false, __ATOMIC_RELEASE);
            (void)nrf_sdh_request_continue();
        }
        return;
    }
    if (operation.scheduled) return;
    if (operation.finished) {
        uint32_t result = operation.failed ?
            NRF_EVT_FLASH_OPERATION_ERROR : NRF_EVT_FLASH_OPERATION_SUCCESS;
        /* The SoC IRQ can run immediately after it is pended. Release the
         * old slot before its fstorage handler submits a follow-up write. */
        taskENTER_CRITICAL();
        if (r1_cordio_soc_event_publish(result)) {
            memset(&operation, 0, sizeof(operation));
        }
        taskEXIT_CRITICAL();
        return;
    }
    if (!baseband_held) {
        /* The scheduler's time source is disabled when BLE has no active
         * procedures. Keep this hold through subsequent BLE procedures;
         * releasing it after one flash slot could stop a queued BLE BOD. */
        BbStart(BB_PROT_NONE);
        baseband_held = true;
    }
    memset(&flash_bod, 0, sizeof(flash_bod));
    flash_bod.minDurUsec = R1_FLASH_SLOT_US;
    flash_bod.maxDurUsec = R1_FLASH_SLOT_US;
    flash_bod.reschPolicy = BB_RESCH_BACKGROUND;
    flash_bod.protId = BB_PROT_NONE;
    flash_bod.endCback = flash_slot_end;
    flash_bod.abortCback = flash_slot_abort;
    operation.scheduled = true;
    SchInsertNextAvailable(&flash_bod);
}

static uint32_t submit(flash_kind_t kind, uint32_t address,
                       const uint32_t *source, uint32_t words)
{
    if (!storage_layout_valid()) return NRF_ERROR_FORBIDDEN;
    if (!registered) {
        if (nrf_sdh_is_enabled()) return NRF_ERROR_INVALID_STATE;
        if (__atomic_exchange_n(&sync_busy, 1u, __ATOMIC_ACQ_REL) != 0u)
            return NRF_ERROR_BUSY;
        bool success = kind == FLASH_ERASE ?
            nvmc_full_erase(address) : nvmc_write_chunk(address, source, words);
        __atomic_store_n(&sync_busy, 0u, __ATOMIC_RELEASE);
        return success ? NRF_SUCCESS : NRF_ERROR_INTERNAL;
    }
    if (!nrf_sdh_is_enabled()) return NRF_ERROR_INVALID_STATE;
    taskENTER_CRITICAL();
    if (operation.kind != FLASH_NONE) {
        taskEXIT_CRITICAL();
        return NRF_ERROR_BUSY;
    }
    operation.address = address;
    operation.source = source;
    operation.words = words;
    operation.progress = 0u;
    operation.partial_steps = 0u;
    operation.scheduled = false;
    operation.finished = false;
    operation.failed = false;
    __atomic_store_n(&operation.kind, kind, __ATOMIC_RELEASE);
    taskEXIT_CRITICAL();
    return NRF_SUCCESS;
}

uint32_t sd_flash_page_erase(uint32_t page_number)
{
    if (page_number >= 256u)
        return NRF_ERROR_INVALID_ADDR;
    uint32_t address = page_number * R1_FLASH_PAGE_BYTES;
    if (!in_storage(address, R1_FLASH_PAGE_BYTES))
        return NRF_ERROR_FORBIDDEN;
    return submit(FLASH_ERASE, address, 0, 0u);
}

uint32_t sd_flash_write(uint32_t *destination, const uint32_t *source,
                        uint32_t words)
{
    if (((uintptr_t)destination & 3u) != 0u ||
        ((uintptr_t)source & 3u) != 0u || source == 0)
        return NRF_ERROR_INVALID_ADDR;
    if (words == 0u || words > R1_FLASH_PAGE_BYTES / 4u)
        return NRF_ERROR_INVALID_LENGTH;
    if ((uintptr_t)destination >= 0x00100000u)
        return NRF_ERROR_INVALID_ADDR;
    if (!in_storage((uint32_t)(uintptr_t)destination, words * 4u))
        return NRF_ERROR_FORBIDDEN;
    uintptr_t src = (uintptr_t)source;
    if (src < 0x20000000u || src >= 0x20040000u ||
        words * 4u > 0x20040000u - src)
        return NRF_ERROR_INVALID_ADDR;
    return submit(FLASH_WRITE, (uint32_t)(uintptr_t)destination,
                  source, words);
}
#endif
