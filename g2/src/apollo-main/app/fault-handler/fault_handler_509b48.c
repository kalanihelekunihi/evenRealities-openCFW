/* Apollo fault handler 0x509b48, defined-code paths.
 * Native's table search has no visible bound. Unknown-code behavior remains
 * an explicit provider gate rather than an invented fallback. */
#include <stdint.h>

struct audio_fault_record {
    uint32_t type, detail;
    const char *path, *function;
    uint32_t line;
};
struct audio_fault_code_row {uint16_t code, reserved; const char *message;};
_Static_assert(sizeof(struct audio_fault_record)==20u,"fault record ABI");
_Static_assert(sizeof(struct audio_fault_code_row)==8u,"fault row ABI");

extern const struct audio_fault_code_row audio_fault_code_table[43];
extern void audio_uart_buffer_zero(void *,uint32_t,uint32_t);
extern int32_t audio_ble_format_to_buffer(char *,const char *,...); /* native 0x4b4728 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern const char *audio_fault_unmapped_code_message(uint16_t);

static const char module[]="assert";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\utils\\assert\\util_error_check.c";
static const char function[]="APP_errorFaultHandler";
static const char message[]="%s, %s %d, %s";
static const char short_message[]="[assert]%s, %s %d, %s";

void audio_ring_pb_assert_509b48(const struct audio_fault_record *record) {
    char formatted[512];
    audio_uart_buffer_zero(formatted,512u,0u);
    if((uint8_t)record->type==0u) {
        uint16_t code=(uint16_t)record->detail;
        const char *reason=0;
        for(uint32_t i=0;i<43u;i++)
            if(audio_fault_code_table[i].code==code) {
                reason=audio_fault_code_table[i].message;
                break;
            }
        if(reason==0) reason=audio_fault_unmapped_code_message(code);
        (void)audio_ble_format_to_buffer(formatted,"Error code 0x%04X: %s",
                                         (uint32_t)code,reason);
    } else if((uint8_t)record->type==1u) {
        (void)audio_ble_format_to_buffer(formatted,"(%s) is not established.",
                                         (const char *)(uintptr_t)record->detail);
    }
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,0x71u,message,
                           record->path,record->function,record->line,formatted);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x05000000u,short_message,short_message,
                                    record->path,record->function,record->line,formatted);
}
