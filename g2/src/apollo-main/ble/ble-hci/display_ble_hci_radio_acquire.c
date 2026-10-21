/* Native radio resource acquire 0x52dd94. Authenticated ROM slots:
 * 0x52e940 -> live 0x20073dc4; 0x52e944 -> config 0x200001b4;
 * 0x52ea24 -> live 0x20074224. Vendor stack children remain real imports. */
#include <stdint.h>
extern uint8_t audio_ble_hci_radio_resource_state_20073dc4[];
extern const uint8_t audio_ble_hci_radio_resource_config_200001b4[20];
extern volatile uint32_t audio_ble_hci_radio_revision_word_20074224;
extern const uint8_t audio_ble_hci_radio_resource_log_768a90[];
extern const uint8_t audio_ble_hci_radio_resource_log5_77d90c[];
extern const uint8_t audio_ble_hci_radio_resource_revision_log_768aac[];
extern void audio_ble_hci_boot_log_4733ee(const void *,...);
extern void audio_ble_radio_power_config_4c2b68(uint32_t,uint32_t);
extern void audio_ble_radio_platform_init_52dc40(void);
extern int32_t audio_ble_radio_stack_open_55c2bc(uint32_t,void *);
extern int32_t audio_ble_radio_stack_option_55c7e8(uint32_t,uint32_t,uint32_t);
extern int32_t audio_ble_radio_stack_config_55ca94(uint32_t,const void *);
extern int32_t audio_ble_radio_stack_start_55c32e(uint32_t);
extern void audio_ble_radio_context_init_52e0a2(void *);
extern int32_t audio_ble_radio_context_check_52e4b4(void *);
extern void audio_ble_radio_context_recover_52f0f8(void *,uint32_t,uint32_t);
extern int32_t audio_ble_radio_read_revision_52eeea(void *,volatile uint32_t *);
extern void audio_ble_radio_dispatch_set_52edd8(uint32_t);
static uint32_t word(const uint8_t *p) {uint32_t v;__builtin_memcpy(&v,p,4u);return v;}
static void put(uint8_t *p,uint32_t v) {__builtin_memcpy(p,&v,4u);}

uint32_t audio_ble_hci_radio_acquire_52dd94(uint32_t kind,const uint32_t *config,
                                              void **out_context,uint32_t *out_stack) {
    uint8_t *state=audio_ble_hci_radio_resource_state_20073dc4;
    if(state[8u]!=0u||kind>=9u||config==0)return 1u;
    audio_ble_radio_power_config_4c2b68(kind,0u);
    audio_ble_radio_platform_init_52dc40();
    uint8_t stack_config[20];
    for(uint32_t i=0;i<20u;i++)stack_config[i]=audio_ble_hci_radio_resource_config_200001b4[i];
    put(stack_config+12u,config[0]);put(stack_config+16u,config[1]);
    uint32_t stack=0u;
    if(audio_ble_radio_stack_open_55c2bc(kind,&stack)!=0||
       audio_ble_radio_stack_option_55c7e8(stack,0u,0u)!=0||
       audio_ble_radio_stack_config_55ca94(stack,stack_config)!=0||
       audio_ble_radio_stack_start_55c32e(stack)!=0)return 1u;
    state[8u]=1u;state[9u]=1u;
    put(state,kind);put(state+4u,stack);
    *out_stack=stack;
    *out_context=(void *)state;
    audio_ble_radio_context_init_52e0a2(state);
    int32_t check=audio_ble_radio_context_check_52e4b4(state);
    audio_ble_hci_boot_log_4733ee(audio_ble_hci_radio_resource_log_768a90,check);
    if(check==5||check==0) {
        if(check==5)audio_ble_hci_boot_log_4733ee(audio_ble_hci_radio_resource_log5_77d90c);
        audio_ble_radio_context_recover_52f0f8(state,7u,check==5);
    }
    int32_t result=audio_ble_radio_read_revision_52eeea(
        state,&audio_ble_hci_radio_revision_word_20074224);
    uint32_t revision=audio_ble_hci_radio_revision_word_20074224;
    if(result==0&&revision!=0xffffffffu)
        audio_ble_hci_boot_log_4733ee(audio_ble_hci_radio_resource_revision_log_768aac,
            revision>>24,(revision>>16)&0xffu,(revision>>8)&0xffu,(uint8_t)revision);
    audio_ble_radio_dispatch_set_52edd8(0u);
    return 0u;
}
