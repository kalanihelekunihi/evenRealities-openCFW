/* Bounded BLE event handoff from the source Cordio DFU host to Nordic's
 * polling observer. The bootloader owns this RAM while the application is
 * absent; the lower controller's event callback is the sole producer. */
#if defined(SVCALL_AS_NORMAL_FUNCTION)
#include <stdbool.h>
#include <stdint.h>
#include <string.h>
#include "ble.h"
#include "nrf.h"
#include "nrf_error.h"
#include "cordio_ble_events.h"

enum {
    R1_DFU_EVENT_SLOTS = 4,
    R1_DFU_EVENT_BYTES = BLE_EVT_LEN_MAX(247)
};
_Static_assert(R1_DFU_EVENT_BYTES <= 500u,
               "Nordic DFU observer buffer must hold Cordio BLE events");

typedef struct {
    uint16_t length;
    uint32_t words[(R1_DFU_EVENT_BYTES + 3u) / 4u];
} r1_dfu_event_slot_t;

static r1_dfu_event_slot_t slots[R1_DFU_EVENT_SLOTS];
static uint8_t write_index;
static uint8_t read_index;

bool r1_bootloader_ble_event_publish(const void *event, uint16_t length)
{
    if (event == 0 || length < sizeof(ble_evt_hdr_t) ||
        length > R1_DFU_EVENT_BYTES ||
        ((const ble_evt_t *)event)->header.evt_len != length)
        return false;
    uint8_t write = __atomic_load_n(&write_index, __ATOMIC_RELAXED);
    uint8_t read = __atomic_load_n(&read_index, __ATOMIC_ACQUIRE);
    if ((uint8_t)(write - read) >= R1_DFU_EVENT_SLOTS)
        return false;
    r1_dfu_event_slot_t *slot = &slots[write % R1_DFU_EVENT_SLOTS];
    memcpy(slot->words, event, length);
    slot->length = length;
    __atomic_store_n(&write_index, (uint8_t)(write + 1u), __ATOMIC_RELEASE);
    __SEV();
    return true;
}

uint32_t sd_ble_evt_get(uint8_t *destination, uint16_t *length)
{
    if (length == 0 || ((uintptr_t)length & 1u) != 0u ||
        (destination != 0 &&
         ((uintptr_t)destination & (BLE_EVT_PTR_ALIGNMENT - 1u)) != 0u))
        return NRF_ERROR_INVALID_ADDR;
    uint8_t read = __atomic_load_n(&read_index, __ATOMIC_RELAXED);
    if (read == __atomic_load_n(&write_index, __ATOMIC_ACQUIRE))
        return NRF_ERROR_NOT_FOUND;
    const r1_dfu_event_slot_t *slot = &slots[read % R1_DFU_EVENT_SLOTS];
    uint16_t capacity = *length;
    *length = slot->length;
    if (destination == 0) return NRF_SUCCESS;
    if (capacity < slot->length)
        return NRF_ERROR_DATA_SIZE;
    memcpy(destination, slot->words, slot->length);
    __atomic_store_n(&read_index, (uint8_t)(read + 1u), __ATOMIC_RELEASE);
    return NRF_SUCCESS;
}
#endif
