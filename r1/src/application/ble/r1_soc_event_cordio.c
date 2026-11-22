/* Task-context SoC event queue for the R1 source-built BLE profile. */
#if defined(R1_CORDIO_RTC0)
#include <stdbool.h>
#include <stdint.h>

#include "nrf_error.h"
#include "nrf_soc.h"

extern void WsfTaskLock(void);
extern void WsfTaskUnlock(void);

enum { R1_SOC_EVENT_CAPACITY = 8 };
static uint32_t events[R1_SOC_EVENT_CAPACITY];
static uint8_t read_index;
static uint8_t write_index;

bool r1_cordio_soc_event_publish(uint32_t event_id)
{
    bool accepted = false;
    WsfTaskLock();
    if ((uint8_t)(write_index - read_index) < R1_SOC_EVENT_CAPACITY) {
        events[write_index % R1_SOC_EVENT_CAPACITY] = event_id;
        ++write_index;
        accepted = true;
    }
    WsfTaskUnlock();
    if (accepted) NVIC_SetPendingIRQ(SD_EVT_IRQn);
    return accepted;
}

uint32_t sd_evt_get(uint32_t *event_id)
{
    if (event_id == 0 || ((uintptr_t)event_id & 3u) != 0u)
        return NRF_ERROR_INVALID_ADDR;
    uint32_t result = NRF_ERROR_NOT_FOUND;
    WsfTaskLock();
    if (read_index != write_index) {
        *event_id = events[read_index % R1_SOC_EVENT_CAPACITY];
        ++read_index;
        result = NRF_SUCCESS;
    }
    WsfTaskUnlock();
    return result;
}
#endif
