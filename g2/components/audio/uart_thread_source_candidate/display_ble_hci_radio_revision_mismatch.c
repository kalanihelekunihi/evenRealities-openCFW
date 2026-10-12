/* Native 0x4b47cc. Literal cells 0x4b4d44/48 resolve to these exact strings. */
#include <stdint.h>

extern int32_t audio_ble_hci_boot_log_4733ee(const char *,...);

uint32_t audio_ble_hci_radio_revision_mismatch_4b47cc(uint32_t radio,
                                                        uint32_t required)
{
    static const char needs_update[] =
        "need updata em9305 firmware 0x%x, 0x%x \r\n";
    static const char current[] =
        "NOT need updata em9305 firmware 0x%x, 0x%x \r\n";
    for (int index = 3; index >= 0; --index) {
        unsigned shift = (unsigned)index * 8u;
        if (((radio >> shift) & 0xffu) < ((required >> shift) & 0xffu)) {
            /* Native leaves the required revision in R2 at the log call. */
            audio_ble_hci_boot_log_4733ee(needs_update,radio,required);
            return 1u;
        }
    }
    audio_ble_hci_boot_log_4733ee(current,radio,required);
    return 0u;
}
