/* Terminal host-readiness check, native 0x5eca84..0x5ecaab (session-list
 * helpers next to the session count 0x5eca48; no source path retained).
 * Used by the session-list selector 0x5ed152: true only while BLE is
 * connected and the host reports HOST_STATUS_STREAMING. */
#include <stdint.h>

#define TD_HOST_STATUS 0xa1d8u
#define HOST_STATUS_STREAMING 2u

extern uint8_t *audio_td_state_ptr_alias1(void); /* 0x597344 td_state_ptr_alias1 */
extern uint8_t UX_GetSystemBLEStatus(void);

uint8_t terminal_host_streaming_ready_5eca84(void)
{
    const uint8_t *td = audio_td_state_ptr_alias1();
    if (UX_GetSystemBLEStatus() == 0u || td == 0 || td[TD_HOST_STATUS] != HOST_STATUS_STREAMING)
        return 0u;
    return 1u;
}
