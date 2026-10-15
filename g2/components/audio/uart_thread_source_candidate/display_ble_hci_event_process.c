/* Native hciEvtProcessMsg 0x56b390. Event size/decoder tables are ROM data. */
#include <stdint.h>

extern uint8_t audio_ble_hci_stack_state_20073870[]; /* live */
extern volatile uint16_t audio_ble_hci_event_counts_20073bc0[]; /* live */
extern const uint8_t audio_ble_hci_event_sizes_6e3720[];
extern const uint32_t audio_ble_hci_event_decoders_6c910c[];
extern const uint8_t audio_ble_hci_vendor_tag_78d6f4[];
extern const uint8_t audio_ble_hci_vendor_tag2_78d6fc[];
extern const uint8_t audio_ble_hci_vendor_ere[]; /* ROM 0x56b7bc */
extern const uint8_t audio_ble_hci_vendor_app[]; /* ROM 0x56b7c0 */
extern const uint8_t audio_ble_hci_vendor_hci[]; /* ROM 0x56b7c4 */
extern const uint8_t audio_ble_hci_vendor_message_77f720[];
extern const uint8_t audio_ble_hci_vendor_file_77f70c[];
extern const uint8_t audio_ble_hci_vendor_file_6e0518[];

extern uint32_t audio_ble_hci_cis_by_handle(uint32_t);
extern void audio_ble_hci_event_cmd_complete(const void *,uint32_t);
extern void audio_ble_hci_event_cmd_status(const void *);
extern void audio_ble_hci_num_complete_packets(const void *);
extern void audio_ble_hci_conn_open(uint32_t);
extern void audio_ble_hci_conn_close(uint32_t);
extern void audio_ble_hci_cis_open(uint32_t);
extern void audio_ble_hci_cis_close(uint32_t);
extern void audio_ble_hci_le_adv_report(const void *,uint32_t);
extern void audio_ble_hci_le_direct_adv_report(const void *,uint32_t);
extern void audio_ble_hci_le_ext_adv_report(const void *,uint32_t);
extern void audio_ble_hci_le_per_adv_report(const void *,uint32_t);
extern void audio_ble_hci_le_conless_iq_report(const void *,uint32_t);
extern void audio_ble_hci_le_conn_iq_report(const void *,uint32_t);
extern void *audio_wsf_buffer_alloc(uint16_t); /* selected WsfBufAlloc */
extern void g2_wsf_candidate_buffer_free_word(uint32_t); /* selected WsfBufFree */
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern uint32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern void audio_ble_hci_wsf_trace(const void *,const void *);

static uint16_t word(const uint8_t *p) { return (uint16_t)((uint16_t)p[0]|((uint16_t)p[1]<<8)); }
static uint32_t pointer(const uint8_t *p) { uint32_t v; __builtin_memcpy(&v,p,4u);return v; }
static void deliver_vendor_diagnostic(uint32_t *low,uint32_t *high) {
    const void *tag=audio_ble_hci_vendor_tag_78d6f4;
    const void *file=audio_ble_hci_vendor_file_6e0518;
    const void *detail=audio_ble_hci_vendor_file_77f70c;
    uint32_t category=0u;
    if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u &&
       audio_ble_hci_vendor_compare_44b610(tag,audio_ble_hci_vendor_ere,3u)==0u)
        category=1u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u &&
            audio_ble_hci_vendor_compare_44b610(tag,audio_ble_hci_vendor_tag2_78d6fc,4u)==0u)
        category=2u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u &&
            audio_ble_hci_vendor_compare_44b610(tag,tag,4u)==0u)
        category=3u;
    else if(audio_ble_hci_vendor_log_enabled_4c9c50()!=0u) {
        if((audio_log_flags()&2u)!=0u)category=4u;
    } else if(audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
              audio_ble_hci_vendor_compare_44b610(audio_ble_hci_vendor_app,
                                                   audio_ble_hci_vendor_hci,3u)!=0u) {
        audio_ble_hci_wsf_trace(tag,audio_ble_hci_vendor_message_77f720);
    }
    if(category!=0u && (audio_log_flags()&2u)!=0u) {
        *low=0xb0fu;
        *high=(uint32_t)(uintptr_t)audio_ble_hci_vendor_message_77f720;
        audio_log_extended((uint8_t)category,
                           (const char *)audio_ble_hci_vendor_app,
                           (const char *)file,(const char *)detail,
                           *low,(const char *)(uintptr_t)*high);
    }
}

uint64_t audio_ble_hci_event_process_body(const void *message,uint32_t unused,
                                           uint32_t low,uint32_t high) {
    (void)unused;
    const uint8_t *p=(const uint8_t *)message;
    uint8_t code=p[0],length=p[1],type=0u;
    const uint8_t *data=p+2u;
    uint32_t callback=pointer(audio_ble_hci_stack_state_20073870+8u);
    switch(code) {
    case 0x05u:
        audio_ble_hci_event_counts_20073bc0[0]++;
        type=audio_ble_hci_cis_by_handle(word(p+3u))==0u?3u:0x46u;
        break;
    case 0x08u: audio_ble_hci_event_counts_20073bc0[1]++;type=0x0fu;break;
    case 0x0cu: audio_ble_hci_event_counts_20073bc0[2]++;type=10u;break;
    case 0x0eu:
        audio_ble_hci_event_counts_20073bc0[3]++;
        audio_ble_hci_event_cmd_complete(data,length);break;
    case 0x0fu:
        audio_ble_hci_event_counts_20073bc0[4]++;
        audio_ble_hci_event_cmd_status(data);break;
    case 0x10u: audio_ble_hci_event_counts_20073bc0[5]++;type=0x14u;break;
    case 0x13u:
        audio_ble_hci_num_complete_packets(data);
        audio_ble_hci_event_counts_20073bc0[6]++;break;
    case 0x1au: audio_ble_hci_event_counts_20073bc0[7]++;break;
    case 0x30u: audio_ble_hci_event_counts_20073bc0[8]++;type=0x0eu;break;
    case 0x3eu: {
        uint8_t sub=data[0];data=p+3u;
        audio_ble_hci_event_counts_20073bc0[9]++;
        switch(sub) {
        case 1u: if(data[0]==0u)audio_ble_hci_conn_open(word(p+4u));type=1u;break;
        case 2u: audio_ble_hci_le_adv_report(data,length);break;
        case 3u:type=4u;break; case 4u:type=0x0bu;break;
        case 5u:type=0x10u;break; case 6u:type=0x23u;break;
        case 7u:type=0x24u;break;
        case 8u:callback=pointer(audio_ble_hci_stack_state_20073870+0x0cu);type=0x25u;break;
        case 9u:callback=pointer(audio_ble_hci_stack_state_20073870+0x0cu);type=0x26u;break;
        case 10u:if(data[0]==0u)audio_ble_hci_conn_open(word(p+4u));type=2u;break;
        case 11u:audio_ble_hci_le_direct_adv_report(data,length);break;
        case 12u:type=0x2bu;break;
        case 13u:audio_ble_hci_le_ext_adv_report(data,length);break;
        case 14u:type=0x30u;break;
        case 15u:audio_ble_hci_le_per_adv_report(data,length);break;
        case 16u:type=0x32u;break; case 17u:type=0x2du;break;
        case 18u:type=0x2eu;break; case 19u:type=0x2fu;break;
        case 21u:audio_ble_hci_le_conless_iq_report(data,length);break;
        case 22u:audio_ble_hci_le_conn_iq_report(data,length);break;
        case 23u:deliver_vendor_diagnostic(&low,&high);break;
        case 25u:if(data[0]==0u)audio_ble_hci_cis_open(word(p+4u));type=0x44u;break;
        case 26u:type=0x45u;break; case 27u:type=0x50u;break;
        case 28u:type=0x51u;break; case 29u:type=0x52u;break;
        case 30u:type=0x53u;break; case 31u:type=0x47u;break;
        case 34u:type=0x55u;break;
        default:break;
        }
        break;
    }
    case 0x57u:audio_ble_hci_event_counts_20073bc0[11]++;type=0x28u;break;
    case 0xffu:audio_ble_hci_event_counts_20073bc0[10]++;type=0x13u;break;
    default:break;
    }
    if(type!=0u) {
        uint16_t bytes=audio_ble_hci_event_sizes_6e3720[type];
        uint8_t *event=(uint8_t *)audio_wsf_buffer_alloc(bytes);
        if(event!=0) {
            event[0]=0u;event[1]=0u;event[2]=type;event[3]=0u;
            uint32_t decoder=audio_ble_hci_event_decoders_6c910c[type];
            ((void (*)(void *,const void *,uint32_t))(uintptr_t)decoder)(event,data,length);
            ((void (*)(void *))(uintptr_t)callback)(event);
            g2_wsf_candidate_buffer_free_word((uint32_t)(uintptr_t)event);
        }
        if(type==3u)audio_ble_hci_conn_close(word(data+1u));
        else if(type==0x46u)audio_ble_hci_cis_close(word(data+1u));
    }
    return ((uint64_t)high<<32)|low;
}

__attribute__((naked)) uint64_t audio_ble_hci_event_process(const void *message) {
    __asm volatile("b audio_ble_hci_event_process_body");
}
