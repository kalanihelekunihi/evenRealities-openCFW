/* Native Cordio hciEvtProcessLeConlessIQReport 0x56a908. */
#include <stdint.h>
#include <stddef.h>
extern void *audio_wsf_buffer_alloc(uint16_t);
extern void g2_wsf_candidate_buffer_free_word(uint32_t);
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t);
extern uint32_t audio_ble_hci_vendor_log_enabled_4c9c50(void);
extern uint32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_ble_hci_vendor_log_43d574(uint32_t,const void *,const void *,const void *,...);
extern void audio_ble_hci_wsf_trace(const void *,const void *);
extern uint8_t audio_ble_hci_stack_state_20073870[]; /* live state callback slot +8 */
const uint8_t audio_ble_hci_vendor_tag_78d6f4[]="INFO"; /* ROM 0x78d6f4 */
const uint8_t audio_ble_hci_vendor_tag2_78d6fc[]="WARN"; /* ROM 0x78d6fc */
const uint8_t audio_ble_hci_vendor_ere[]="ERR"; /* ROM 0x56a968 */
const uint8_t audio_ble_hci_vendor_app[]="APP"; /* ROM 0x56abd0 */
const uint8_t audio_ble_hci_vendor_hci[]="HCI"; /* ROM 0x56aa2c */
static const char file[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-host\\sources\\hci\\ambiq\\hci_evt.c";
static const char function[]="hciEvtProcessLeConlessIQReport";
static const char message[]="rcv Le Conntless IQ Report...";
static void diagnostic(void)
{
    const uint8_t *info=audio_ble_hci_vendor_tag_78d6f4;
    const uint8_t *warn=audio_ble_hci_vendor_tag2_78d6fc;
    const uint8_t *error=audio_ble_hci_vendor_ere;
    const uint8_t *app=audio_ble_hci_vendor_app;
    const uint8_t *hci=audio_ble_hci_vendor_hci;
    uint32_t level=0u;
    if (audio_ble_hci_vendor_log_enabled_4c9c50()!=0u &&
        audio_ble_hci_vendor_compare_44b610(info,error,3u)==0u) level=1u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50()!=0u &&
             audio_ble_hci_vendor_compare_44b610(info,warn,4u)==0u) level=2u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50()!=0u &&
             audio_ble_hci_vendor_compare_44b610(info,info,4u)==0u) level=3u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50()!=0u) level=4u;
    else if (audio_ble_hci_vendor_log_enabled_4c9c50()==0u ||
             audio_ble_hci_vendor_compare_44b610(app,hci,3u)!=0u) {
        audio_ble_hci_wsf_trace(info,message);
        return;
    }
    if ((audio_log_flags()&2u)!=0u)
        audio_ble_hci_vendor_log_43d574(level,app,file,function,0x690u,message);
}
void audio_ble_hci_le_conless_iq_report(const void *event,uint32_t length)
{
    (void)length; /* native parser uses the reported sample count at byte 11 */
    const uint8_t *src=(const uint8_t *)event;
    uint8_t *out=(uint8_t *)audio_wsf_buffer_alloc(0xc0u);
    if (out==0) return;
    diagnostic();
    out[4]=src[0];out[5]=src[1];out[6]=src[2];
    out[8]=src[3];out[9]=src[4];out[10]=src[5];out[11]=src[6];
    out[12]=src[7];out[13]=src[8];out[14]=src[9];out[15]=src[10];
    out[16]=src[11];
    uint32_t first=(uint32_t)(uintptr_t)(out+28u);
    uint32_t second=(uint32_t)(uintptr_t)(out+110u);
    __builtin_memcpy(out+20u,&first,4u);
    audio_queue_copy_bytes(out+28u,src+12u,out[16]);
    __builtin_memcpy(out+24u,&second,4u);
    /* The second native 0x439be4 call also loads the first pointer at +20. */
    audio_queue_copy_bytes(out+28u,src+12u+out[16],out[16]);
    out[0]=out[4];out[1]=out[5];out[3]=out[13];out[2]=0x56u;
    uintptr_t callback;
    __builtin_memcpy(&callback,audio_ble_hci_stack_state_20073870+8u,sizeof(callback));
    ((void (*)(void *))callback)(out);
    g2_wsf_candidate_buffer_free_word((uint32_t)(uintptr_t)out);
}
