/* Native 0x52fc04 deinitializes EM9305 firmware staging state and releases
 * its live buffer. Product RAM cells are reset by this body, not seeded. */
#include <stdint.h>
extern void audio_file_heap_free(void *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="srv.em9305";
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\DFU\\service_em9305_dfu.c";
static const char function[]="SVC_Em9305FwDeinit";
static const char free_message[]="free g_file_buffer success";
static const char free_compact[]="[srv.em9305]free g_file_buffer success";
static const char done_message[]="BLE firmware data deinitialized";
static const char done_compact[]="[srv.em9305]BLE firmware data deinitialized";
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
#define B(a) (*(volatile uint8_t *)(uintptr_t)(a))
static void log_event(uint32_t line,const char *message,const char *compact) {
    if(audio_log_flags()&2u)
        audio_log_extended(4u,module,source_path,function,line,message);
    if((audio_log_flags()&1u)||(audio_log_flags()&4u))
        (void)compressed_log_output(0x10000000u,compact,compact);
}
void audio_ble_hci_radio_finalize_52fc04(void) {
    if(W(0x2007494cu)!=0u) {
        audio_file_heap_free((void *)(uintptr_t)W(0x2007494cu));
        log_event(0x162u,free_message,free_compact);
        W(0x2007494cu)=0u;
        W(0x20074950u)=0u;
    }
    __builtin_memset((void *)(uintptr_t)0x200731f0u,0,0x40u);
    __builtin_memset((void *)(uintptr_t)0x2007348cu,0,0x30u);
    W(0x20074958u)=0u;
    W(0x2007495cu)=0u;
    W(0x20074960u)=0u;
    W(0x20074964u)=0u;
    B(0x20075016u)=0u;
    log_event(0x177u,done_message,done_compact);
}
