/* Connected pinned Cordio SMP/WSF action descendants, authenticated against
 * stock Main decompilation at 0x537bca, 0x56cf04 and 0x52a4b8.
 * HCI_TX_DATA_TAILROOM is zero in this build; the stock smpMsgAlloc passes
 * R1=0 to WsfMsgDataAlloc. The selected C allocator has that exact ABI. */
#include <stdint.h>

extern void *audio_ble_hci_msg_data_alloc(uint16_t length, uint8_t prefix);
extern void *WsfBufAlloc(uint16_t length);
extern void smpSmExecute(void *ccb, void *message);
extern void audio_ble_wsf_timer_insert(void *timer, uint32_t ticks);

void *smpMsgAlloc(uint16_t length) {
    return audio_ble_hci_msg_data_alloc(length, 0u);
}

uint8_t *SmpScAlloc(uint8_t size, void *ccb, uint8_t *message) {
    uint8_t *buffer = WsfBufAlloc(size);
    if (buffer == 0) {
        message[3] = 8u; /* SMP_ERR_UNSPECIFIED */
        message[2] = 3u; /* SMP_MSG_API_CANCEL_REQ */
        smpSmExecute(ccb, message);
    }
    return buffer;
}

void WsfTimerStartSec(void *timer, uint32_t seconds) {
    audio_ble_wsf_timer_insert(timer, seconds * 100u);
}
