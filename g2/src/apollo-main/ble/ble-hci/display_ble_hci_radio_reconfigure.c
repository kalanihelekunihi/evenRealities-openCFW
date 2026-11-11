/* Native 0x4b480a retry/reconfigure parent. Product cells are live RAM
 * authenticated by literals 0x4b4d4c..0x4b4d60; no seed is invented. */
#include <stdint.h>
/* Stock-RAM literals rewritten to named objects (sim-test wave 2026-10-26,
 * .waves/sim-fix/apply.py): g2ref_X is the linker symbol X. */
#include <stdint.h>
extern unsigned char g2ref_audio_ble_hci_radio_revision_cell[] __asm__("audio_ble_hci_radio_revision_cell");
extern unsigned char g2ref_g2_stock_ram_200036d8[] __asm__("g2_stock_ram_200036d8");
extern unsigned char g2ref_g2_stock_ram_20074948[] __asm__("g2_stock_ram_20074948");
extern uint32_t audio_ble_radio_configure_52e5ce(void *,uint32_t,uint32_t);
extern uint32_t audio_ble_radio_tune_52e5f2(uint32_t,uint32_t);
extern int32_t audio_ble_radio_attempt_52edf0(void *,uint32_t);
extern void audio_ble_radio_commit_52eefa(void *,uint32_t);
extern void audio_ble_radio_ready_44b0ae(void);
extern int32_t audio_ble_radio_context_check_52e4b4(void *);
extern void audio_ble_radio_dispatch_set_52edd8(uint32_t);
extern void audio_ble_hci_boot_log_4733ee(const char *,...);
/* NUL-terminated literals authenticated at stock 0x777984/0x7602d0. */
const char audio_ble_hci_radio_reconfigure_ok_log_777984[] =
    "Update image success \r\n";
const char audio_ble_hci_radio_reconfigure_fail_log_7602d0[] =
    "Update image fail, status:%d\r\n";
#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))
uint32_t audio_ble_hci_radio_reconfigure_4b480a(void *context,uint32_t r1,
                                                uint32_t r2,uint32_t r3) {
    (void)r1;(void)r2;
    (void)audio_ble_radio_configure_52e5ce((void *)(uintptr_t)((uint32_t)(uintptr_t)g2ref_g2_stock_ram_200036d8+0x4u),4u,
                                            U32(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074948+0x28u)));
    (void)audio_ble_radio_tune_52e5f2(U32(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074948+0x24u)),U32(((uint32_t)(uintptr_t)g2ref_g2_stock_ram_20074948+0x20u))&0xffu);
    uint8_t attempts=0u;
    int32_t result;
    do {
        attempts++;
        result=audio_ble_radio_attempt_52edf0(context,1u);
        if(result==0) {
            audio_ble_hci_boot_log_4733ee(audio_ble_hci_radio_reconfigure_ok_log_777984);
            audio_ble_radio_commit_52eefa(context,U32(((uint32_t)(uintptr_t)g2ref_audio_ble_hci_radio_revision_cell)));
            audio_ble_radio_ready_44b0ae();
            (void)audio_ble_radio_context_check_52e4b4(context);
        } else {
            audio_ble_hci_boot_log_4733ee(audio_ble_hci_radio_reconfigure_fail_log_7602d0,result);
            audio_ble_radio_dispatch_set_52edd8(1u);
        }
    } while(attempts<2u && result!=0);
    return r3;
}
