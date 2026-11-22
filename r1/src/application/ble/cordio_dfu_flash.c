/* Radio-arbitrated NVMC service for the source BLE DFU bootloader.
 * This object and its state live below the application image: the bootloader
 * never calls the application's FreeRTOS-backed flash owner. */
#if defined(R1_CORDIO_RTC0)
#include <stdbool.h>
#include <stdint.h>
#include <string.h>

#include "nrf.h"
#include "nrf_error.h"
#include "nrf_soc.h"
#include "bb_api.h"
#include "pal_bb.h"
#include "sch_api.h"
#include "wsf_os.h"
#include "cordio_dfu_flash.h"
#include "r1_soc_event_cordio.h"

enum {
    PAGE_BYTES = 4096u,
    IMAGE_BEGIN = 0x00027000u,
    BOOT_BEGIN = 0x000f8000u,
    PARAMS_BEGIN = 0x000fe000u,
    FLASH_END = 0x00100000u,
    WORDS_PER_SLOT = 4u,
    ERASE_STEP_MS = 1u,
    ERASE_MIN_STEPS = 90u,
    ERASE_MAX_STEPS = 160u,
    SLOT_US = 2500u
};

typedef enum { OP_IDLE, OP_WRITE, OP_ERASE } operation_kind_t;
typedef struct {
    operation_kind_t kind;
    uint32_t address;
    const uint32_t *source;
    uint32_t words;
    uint32_t progress;
    uint16_t erase_steps;
    bool scheduled;
    bool finished;
    bool failed;
} operation_t;

static operation_t operation;
static BbOpDesc_t flash_bod;
static bool registered;
static bool baseband_held;

static bool layout_valid(void)
{
    return *(volatile const uint32_t *)0x10000010u == PAGE_BYTES &&
           *(volatile const uint32_t *)0x10000014u == 256u &&
           *(volatile const uint32_t *)0x10001014u == BOOT_BEGIN;
}

static bool writable(uint32_t address, uint32_t bytes)
{
    if (address >= FLASH_END) return false;
    if (bytes == 0u || bytes > FLASH_END - address) return false;
    return (address >= IMAGE_BEGIN && address < BOOT_BEGIN &&
            bytes <= BOOT_BEGIN - address) ||
           (address >= PARAMS_BEGIN && address < FLASH_END);
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

static bool page_erased(uint32_t address)
{
    const volatile uint32_t *p = (const volatile uint32_t *)address;
    for (uint32_t i = 0; i < PAGE_BYTES / 4u; ++i)
        if (p[i] != UINT32_MAX) return false;
    return true;
}

static void erase_step(uint32_t address)
{
    NRF_NVMC->CONFIG = NVMC_CONFIG_WEN_Een;
    __DSB();
    __ISB();
    NRF_NVMC->ERASEPAGEPARTIALCFG = ERASE_STEP_MS;
    NRF_NVMC->ERASEPAGEPARTIAL = address;
    nvmc_wait();
    nvmc_read_mode();
}

static bool write_chunk(uint32_t address, const uint32_t *source,
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
    if (operation.kind == OP_ERASE) {
        erase_step(operation.address);
        ++operation.erase_steps;
        if (operation.erase_steps >= ERASE_MIN_STEPS &&
            page_erased(operation.address))
            operation.finished = true;
        else if (operation.erase_steps >= ERASE_MAX_STEPS) {
            operation.failed = true;
            operation.finished = true;
        }
    } else if (operation.kind == OP_WRITE) {
        uint32_t remaining = operation.words - operation.progress;
        uint32_t count = remaining < WORDS_PER_SLOT ? remaining : WORDS_PER_SLOT;
        uint32_t offset = operation.progress;
        if (!write_chunk(operation.address + offset * 4u,
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

static void protocol_start(void) { }
static void protocol_stop(void) { }
static void protocol_cancel(BbOpDesc_t *bod) { (void)bod; }

void r1_cordio_dfu_flash_register(void)
{
    if (registered) return;
    BbRegisterProt(BB_PROT_NONE, flash_slot, protocol_cancel,
                   protocol_start, protocol_stop);
    registered = true;
}

void r1_cordio_dfu_flash_service(void)
{
    if (!registered || operation.kind == OP_IDLE || operation.scheduled)
        return;
    if (operation.finished) {
        uint32_t result = operation.failed ? NRF_EVT_FLASH_OPERATION_ERROR :
                                             NRF_EVT_FLASH_OPERATION_SUCCESS;
        /* The DFU bootloader polls SoC observers after this service returns.
         * Retain the operation until the bounded event queue accepts it. */
        if (r1_cordio_soc_event_publish(result))
            memset(&operation, 0, sizeof(operation));
        return;
    }
    if (!baseband_held) {
        BbStart(BB_PROT_NONE);
        baseband_held = true;
    }
    memset(&flash_bod, 0, sizeof(flash_bod));
    flash_bod.minDurUsec = SLOT_US;
    flash_bod.maxDurUsec = SLOT_US;
    flash_bod.reschPolicy = BB_RESCH_BACKGROUND;
    flash_bod.protId = BB_PROT_NONE;
    flash_bod.endCback = flash_slot_end;
    flash_bod.abortCback = flash_slot_abort;
    operation.scheduled = true;
    SchInsertNextAvailable(&flash_bod);
}

static uint32_t submit(operation_kind_t kind, uint32_t address,
                       const uint32_t *source, uint32_t words)
{
    if (!layout_valid()) return NRF_ERROR_FORBIDDEN;
    if (!registered) return NRF_ERROR_INVALID_STATE;
    WsfTaskLock();
    if (operation.kind != OP_IDLE) {
        WsfTaskUnlock();
        return NRF_ERROR_BUSY;
    }
    operation.address = address;
    operation.source = source;
    operation.words = words;
    operation.progress = 0u;
    operation.erase_steps = 0u;
    operation.scheduled = false;
    operation.finished = false;
    operation.failed = false;
    operation.kind = kind;
    WsfTaskUnlock();
    return NRF_SUCCESS;
}

uint32_t r1_cordio_dfu_flash_erase(uint32_t page_number)
{
    if (page_number >= 256u) return NRF_ERROR_INVALID_ADDR;
    uint32_t address = page_number * PAGE_BYTES;
    if (!writable(address, PAGE_BYTES)) return NRF_ERROR_FORBIDDEN;
    return submit(OP_ERASE, address, 0, 0u);
}

uint32_t r1_cordio_dfu_flash_write(uint32_t *destination,
                                   const uint32_t *source, uint32_t words)
{
    uintptr_t dst = (uintptr_t)destination;
    uintptr_t src = (uintptr_t)source;
    if ((dst & 3u) != 0u || (src & 3u) != 0u || source == 0 ||
        dst >= FLASH_END) return NRF_ERROR_INVALID_ADDR;
    if (words == 0u || words > PAGE_BYTES / 4u)
        return NRF_ERROR_INVALID_LENGTH;
    if (!writable((uint32_t)dst, words * 4u)) return NRF_ERROR_FORBIDDEN;
    if (src < 0x20000000u || src >= 0x20040000u ||
        words * 4u > 0x20040000u - src)
        return NRF_ERROR_INVALID_ADDR;
    return submit(OP_WRITE, (uint32_t)dst, source, words);
}
#endif
