/* Native 0x52eba8 reports each tenth of the update percentage. Valid
 * callers pass a nonzero total size; stock divides by that value directly. */
#include <stdint.h>
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
static const char progress_text[]="Sending %d %%\n"; /* stock 0x784bc0 */
void audio_ble_radio_progress_52eba8(uint32_t processed,uint32_t total) {
    uint32_t percentage=(processed*100u)/total;
    if(percentage%10u==0u) audio_ble_hci_boot_log_4733ee(progress_text,percentage);
}
