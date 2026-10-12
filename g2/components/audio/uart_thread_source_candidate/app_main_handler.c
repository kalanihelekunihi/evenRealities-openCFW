/* Native Packetcraft AppHandler 0x4bae84 and app event children
 * 0x4bacc8/0x4bda34. Callback cells are live, registered app state. */
#include <stdint.h>
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern int32_t audio_l2c_strncmp(const char *,const char *,uint32_t);
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);
extern void (*audio_ble_subsystem_primary_callback_slot)(void *); /* live 0x200740fc */
extern void (*audio_ble_subsystem_callback_slot)(void *); /* live 0x20074100 */
extern uintptr_t audio_ble_ui_callback_cells[]; /* live 0x20073f60, reset callback at +8 */
extern void DmReadRemoteFeatures(uint8_t); /* native 0x4b6cb0 */
static const char info[]="INFO",warn[]="WARN",err[]="ERR",hci[]="HCI",module[]="APP";
static const char message[]="App got evt %d";
static const char function_name[]="AppHandler";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_main.c";

__attribute__((naked))
uint32_t audio_ble_app_reset_callback_4bda34(void){
    __asm__ volatile(
        "push {r7, lr}\n"
        "ldr r1, =audio_ble_ui_callback_cells\n"
        "ldr r0, [r1, #8]\n"
        "cmp r0, #0\n"
        "beq 1f\n"
        "ldr r0, [r1, #8]\n"
        "blx r0\n"
        "1: pop {r0, pc}\n");
}

__attribute__((naked))
uint32_t audio_ble_app_link_event_4bacc8(const uint8_t *event __attribute__((unused))){
    __asm__ volatile(
        "push {r7, lr}\n"
        "ldrb r1, [r0, #2]\n"
        "cmp r1, #0\n"
        "beq 1f\n"
        "cmp r1, #2\n"
        "bne 2f\n"
        "ldrh r0, [r0]\n"
        "uxtb r0, r0\n"
        "bl DmReadRemoteFeatures\n"
        "b 2f\n"
        "1: bl audio_ble_app_reset_callback_4bda34\n"
        "2: pop {r0, pc}\n");
}

uint32_t audio_ble_app_handler_4bae84(uint32_t events,const uint8_t *event){
    if(event!=0){
        uint8_t level=0u;
        if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(info,err,3u)==0)level=1u;
        else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(info,warn,4u)==0)level=2u;
        else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u&&audio_l2c_strncmp(info,info,4u)==0)level=3u;
        else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u)level=4u;
        else if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u||audio_l2c_strncmp(module,hci,3u)!=0)
            audio_ble_wsf_trace(info,message,event[2]);
        if(level!=0u&&(audio_log_level()&2u)!=0u){
            /* Native outgoing IAR varargs overwrite its saved entry R0. */
            events=0xdbu;
            audio_log_extended(level,module,path,function_name,0xdbu,message,event[2]);
        }
        if(event[2]>=0x20u)audio_ble_subsystem_callback_slot((void *)event);
        else if(event[2]>=0x10u)audio_ble_subsystem_primary_callback_slot((void *)event);
        else (void)audio_ble_app_link_event_4bacc8(event);
    }
    return events;
}
