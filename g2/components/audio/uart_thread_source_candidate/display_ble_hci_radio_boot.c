/* Native HciDrvRadioBoot 0x4b48a6; product tables stay typed externs. */
#include <stdint.h>

extern uint8_t audio_ble_hci_radio_boot_config[]; /* live 0x200703ec */
extern volatile uint32_t audio_ble_hci_radio_context_ptr; /* live 0x20074630 */
extern volatile uint32_t audio_ble_hci_radio_aux_ptr; /* live 0x20074634 */
extern volatile uint8_t audio_ble_hci_radio_boot_retry; /* live 0x20074fcc */
extern volatile uint32_t audio_ble_hci_radio_revision_cell; /* live 0x20074954 */
extern volatile uint32_t audio_ble_hci_radio_active; /* live 0x20074638 */
extern volatile uint32_t audio_ble_hci_radio_pending; /* live 0x2007463c */
extern volatile uint32_t audio_ble_hci_radio_command_cell; /* live 0x20074640 */
extern uint8_t audio_ble_hci_radio_driver_state[]; /* live 0x20074148 */
extern uint8_t audio_ble_hci_radio_scheduler_state[]; /* live 0x20073ba8 */
extern uint8_t audio_ble_hci_radio_scheduler_config[]; /* live 0x20065a10 */
extern const uint8_t audio_ble_hci_boot_log_first[]; /* ROM 0x71f5d0 */
extern const uint8_t audio_ble_hci_boot_log_retry[]; /* ROM 0x754ad0 */
extern void opencfw_radio_gpio_callback(void *); /* Thumb entry 0x4b4a99 */

extern uint32_t audio_ble_hci_radio_acquire_52dd94(uint32_t,const void *,void *,void *);
extern uint32_t audio_ble_hci_radio_detect_52deee(void);
extern void audio_ble_hci_boot_log_4733ee(const void *,...);
extern void audio_ble_hci_boot_delay_491102(uint32_t);
extern void audio_ble_hci_radio_prepare_52f38c(void);
extern uint32_t audio_ble_hci_radio_validate_52fcfc(void *);
extern uint32_t audio_ble_hci_radio_revision_52dee6(void);
extern uint32_t audio_ble_hci_radio_revision_mismatch_4b47cc(uint32_t,uint32_t);
extern void audio_ble_hci_radio_recover_52fb58(void);
extern void audio_ble_hci_radio_reconfigure_4b480a(uint32_t);
extern void audio_ble_hci_radio_finalize_52fc04(void);
extern void audio_ble_hci_radio_scheduler_53006c(void *,const void *,uint32_t,uint32_t);
extern void audio_ble_hci_radio_identifier_480d72(uint32_t,void *);
extern void audio_ble_hci_radio_register_48162c(uint32_t,uint32_t,const void *,uint32_t);
extern void audio_ble_hci_radio_enable_52dd58(void);
extern void audio_ble_hci_radio_mux_on_4b4786(uint32_t,uint32_t);
extern void audio_ble_hci_radio_mux_request_4b4768(uint32_t);

uint32_t audio_ble_hci_driver_radio_boot(uint8_t with_identifier) {
    uint32_t config[2]={(uint32_t)(uintptr_t)audio_ble_hci_radio_boot_config,0x40u};
    uint32_t context=audio_ble_hci_radio_acquire_52dd94(
        6u,config,(void *)&audio_ble_hci_radio_context_ptr,
        (void *)&audio_ble_hci_radio_aux_ptr);
    uint32_t radio=audio_ble_hci_radio_detect_52deee();
    audio_ble_hci_boot_log_4733ee(audio_ble_hci_boot_log_first,context,(uint8_t)radio);
    audio_ble_hci_boot_delay_491102(100u);
    if(audio_ble_hci_radio_detect_52deee()!=0u) {
        audio_ble_hci_boot_log_4733ee(audio_ble_hci_boot_log_retry);
        audio_ble_hci_radio_boot_retry=1u;
    }
    audio_ble_hci_radio_prepare_52f38c();
    if(audio_ble_hci_radio_validate_52fcfc((void *)&audio_ble_hci_radio_revision_cell)!=0u) {
        uint32_t revision=audio_ble_hci_radio_revision_52dee6();
        if(audio_ble_hci_radio_revision_mismatch_4b47cc(revision,audio_ble_hci_radio_revision_cell)!=0u ||
           audio_ble_hci_radio_boot_retry!=0u) {
            audio_ble_hci_radio_recover_52fb58();
            audio_ble_hci_radio_prepare_52f38c();
            audio_ble_hci_radio_reconfigure_4b480a(audio_ble_hci_radio_context_ptr);
            audio_ble_hci_radio_prepare_52f38c();
            audio_ble_hci_radio_finalize_52fc04();
            audio_ble_hci_radio_boot_retry=0u;
        }
    }
    audio_ble_hci_radio_active=0u;
    audio_ble_hci_radio_pending=0u;
    audio_ble_hci_radio_scheduler_53006c(audio_ble_hci_radio_scheduler_state,
        audio_ble_hci_radio_scheduler_config,0x104u,0x820u);
    audio_ble_hci_radio_command_cell=0u;
    if(with_identifier!=0u) {
        uint8_t identifier[16];
        audio_ble_hci_radio_identifier_480d72(1u,identifier);
        __builtin_memcpy(audio_ble_hci_radio_driver_state,identifier+8u,4u);
        audio_ble_hci_radio_driver_state[4u]=identifier[5u];
        audio_ble_hci_radio_driver_state[5u]=identifier[6u]&0xfcu;
    }
    audio_ble_hci_radio_register_48162c(0u,0x75u,
        (const void *)opencfw_radio_gpio_callback,0u);
    audio_ble_hci_radio_enable_52dd58();
    audio_ble_hci_radio_mux_on_4b4786(0x3bu,4u);
    audio_ble_hci_radio_mux_request_4b4768(0x3bu);
    return context;
}
