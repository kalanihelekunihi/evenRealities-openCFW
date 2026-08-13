#include "openr1_storage.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "cmsis_os2.h"
#include "fal.h"
#include "nrf.h"
#include "nrf_error.h"
#include "nrf_fstorage.h"
#include "nrf_fstorage_sd.h"

#include "openr1/r1_fal_port.h"

#define OPENR1_STORAGE_WAIT_TICKS UINT32_C(5000)
#define OPENR1_FAL_PARTITION_COUNT 7

typedef enum {
    OPENR1_STORAGE_OPERATION_NONE = 0,
    OPENR1_STORAGE_OPERATION_WRITE,
    OPENR1_STORAGE_OPERATION_ERASE,
} openr1_storage_operation;

static void storage_event_handler(nrf_fstorage_evt_t *event);

NRF_FSTORAGE_DEF(nrf_fstorage_t storage_instance) = {
    .evt_handler = storage_event_handler,
};

static osMutexId_t storage_mutex;
static osSemaphoreId_t storage_completion;
static osThreadId_t softdevice_event_thread;
static volatile openr1_storage_operation pending_operation;
static volatile ret_code_t pending_result;
static r1_flash storage_flash;
static bool storage_ready;

static uint32_t physical_flash_end(void) {
    const uint32_t bootloader = NRF_UICR->NRFFW[0];
    if (bootloader != UINT32_MAX) {
        return bootloader;
    }
    return NRF_FICR->CODEPAGESIZE * NRF_FICR->CODESIZE;
}

static bool storage_range_valid(uint32_t offset, size_t length) {
    return length <= UINT32_MAX &&
        offset <= OPENR1_STORAGE_BYTES &&
        (uint32_t)length <= OPENR1_STORAGE_BYTES - offset;
}

static bool storage_lock(void) {
    return storage_ready &&
        osMutexAcquire(storage_mutex, OPENR1_STORAGE_WAIT_TICKS) == osOK;
}

static bool storage_mutation_context_valid(void) {
    const osThreadId_t current = osThreadGetId();
    /* The Nordic completion event is delivered by this thread's
     * nrf_sdh_evts_poll(). Waiting there would deadlock the callback. */
    return __get_IPSR() == 0u && current != NULL &&
        current != softdevice_event_thread;
}

static void storage_unlock(void) {
    (void)osMutexRelease(storage_mutex);
}

static bool storage_read(void *context, uint32_t offset,
                         uint8_t *output, size_t length) {
    (void)context;
    if (!storage_range_valid(offset, length) ||
        (length > 0u && output == NULL) || !storage_lock()) {
        return false;
    }
    if (length > 0u) {
        memcpy(output,
               (const void *)(uintptr_t)(storage_instance.start_addr + offset),
               length);
    }
    storage_unlock();
    return true;
}

static void storage_event_handler(nrf_fstorage_evt_t *event) {
    if (event == NULL || event->p_param != (void *)&pending_operation ||
        pending_operation == OPENR1_STORAGE_OPERATION_NONE) {
        return;
    }
    const bool expected =
        (pending_operation == OPENR1_STORAGE_OPERATION_WRITE &&
         event->id == NRF_FSTORAGE_EVT_WRITE_RESULT) ||
        (pending_operation == OPENR1_STORAGE_OPERATION_ERASE &&
         event->id == NRF_FSTORAGE_EVT_ERASE_RESULT);
    if (!expected) {
        return;
    }
    pending_result = event->result;
    pending_operation = OPENR1_STORAGE_OPERATION_NONE;
    (void)osSemaphoreRelease(storage_completion);
}

static bool storage_wait(ret_code_t submission_result) {
    if (submission_result != NRF_SUCCESS) {
        pending_operation = OPENR1_STORAGE_OPERATION_NONE;
        return false;
    }
    if (osSemaphoreAcquire(storage_completion, osWaitForever) != osOK) {
        pending_operation = OPENR1_STORAGE_OPERATION_NONE;
        return false;
    }
    return pending_result == NRF_SUCCESS;
}

static bool storage_program(void *context, uint32_t offset,
                            const uint8_t *input, size_t length) {
    (void)context;
    if (!storage_range_valid(offset, length) ||
        (length > 0u && input == NULL) ||
        (offset & (sizeof(uint32_t) - 1u)) != 0u ||
        (length & (sizeof(uint32_t) - 1u)) != 0u ||
        ((uintptr_t)input & (sizeof(uint32_t) - 1u)) != 0u ||
        !storage_mutation_context_valid() ||
        !storage_lock()) {
        return false;
    }
    if (length == 0u) {
        storage_unlock();
        return true;
    }
    pending_result = NRF_ERROR_INTERNAL;
    pending_operation = OPENR1_STORAGE_OPERATION_WRITE;
    const ret_code_t submitted = nrf_fstorage_write(
        &storage_instance, storage_instance.start_addr + offset,
        input, (uint32_t)length, (void *)&pending_operation);
    const bool succeeded = storage_wait(submitted);
    storage_unlock();
    return succeeded;
}

static bool storage_erase(void *context, uint32_t offset, size_t length) {
    (void)context;
    if (!storage_range_valid(offset, length) ||
        (offset % R1_FLASH_PAGE_BYTES) != 0u ||
        (length % R1_FLASH_PAGE_BYTES) != 0u ||
        !storage_mutation_context_valid() || !storage_lock()) {
        return false;
    }
    if (length == 0u) {
        storage_unlock();
        return true;
    }
    pending_result = NRF_ERROR_INTERNAL;
    pending_operation = OPENR1_STORAGE_OPERATION_ERASE;
    const ret_code_t submitted = nrf_fstorage_erase(
        &storage_instance, storage_instance.start_addr + offset,
        (uint32_t)(length / R1_FLASH_PAGE_BYTES),
        (void *)&pending_operation);
    const bool succeeded = storage_wait(submitted);
    storage_unlock();
    return succeeded;
}

ret_code_t openr1_storage_initialize(void) {
    if (storage_ready) {
        return NRF_SUCCESS;
    }
    if (NRF_FICR->CODEPAGESIZE != R1_FLASH_PAGE_BYTES) {
        return NRF_ERROR_INVALID_LENGTH;
    }
    const uint32_t flash_end = physical_flash_end();
    const uint32_t physical_bytes =
        NRF_FICR->CODEPAGESIZE * NRF_FICR->CODESIZE;
    if ((flash_end % R1_FLASH_PAGE_BYTES) != 0u ||
        flash_end > physical_bytes || flash_end < OPENR1_STORAGE_BYTES) {
        return NRF_ERROR_INVALID_ADDR;
    }
    storage_mutex = osMutexNew(NULL);
    storage_completion = osSemaphoreNew(1u, 0u, NULL);
    softdevice_event_thread = osThreadGetId();
    if (storage_mutex == NULL || storage_completion == NULL ||
        softdevice_event_thread == NULL) {
        return NRF_ERROR_NO_MEM;
    }
    storage_instance.start_addr = flash_end - OPENR1_STORAGE_BYTES;
    /* nrf_fstorage's implementation treats end_addr as inclusive, despite the
     * SDK 17.1.0 public-header comment calling it exclusive. Keep the
     * bootloader boundary itself out of this instance. */
    storage_instance.end_addr = flash_end - 1u;
    ret_code_t result = nrf_fstorage_init(
        &storage_instance, &nrf_fstorage_sd, NULL);
    if (result != NRF_SUCCESS) {
        return result;
    }
    storage_flash = (r1_flash){
        .context = NULL,
        .size = OPENR1_STORAGE_BYTES,
        .read = storage_read,
        .program = storage_program,
        .erase = storage_erase,
    };
    if (r1_fal_bind(&storage_flash) != R1_OK) {
        return NRF_ERROR_INVALID_STATE;
    }
    storage_ready = true;
    if (fal_init() != OPENR1_FAL_PARTITION_COUNT) {
        storage_ready = false;
        return NRF_ERROR_INTERNAL;
    }
    return NRF_SUCCESS;
}

r1_flash *openr1_storage_flash(void) {
    return storage_ready ? &storage_flash : NULL;
}

uint32_t openr1_storage_start_address(void) {
    return storage_ready ? storage_instance.start_addr : 0u;
}

uint32_t openr1_storage_end_address(void) {
    return storage_ready ? storage_instance.end_addr + 1u : 0u;
}

typedef struct {
    ret_code_t (*initialize)(void);
    r1_flash *(*flash)(void);
    uint32_t (*start_address)(void);
    uint32_t (*end_address)(void);
    r1_error (*export_plan_command)(
        r1_export_state *, const r1_export_observation *, r1_export_plan *);
} openr1_storage_api;

__attribute__((used, section(".openr1_storage_api")))
static const openr1_storage_api retained_storage_api = {
    openr1_storage_initialize,
    openr1_storage_flash,
    openr1_storage_start_address,
    openr1_storage_end_address,
    r1_export_plan_command,
};
