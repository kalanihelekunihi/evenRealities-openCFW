/* Native Packetcraft AppUiAction 0x4bd054: log event and dispatch live UI callback. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern uintptr_t audio_ble_ui_callback_cells[3]; /* live RAM 0x20073f60; reset callback +8 */
static const char module[]="ble.ui";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_ui.c";
static const char function[]="AppUiAction";
#define EVENT(n,line,message) case n: { \
 static const char plain[]=message; \
 static const char compact[]="[ble.ui]" message; \
 if(audio_log_flags()&2u)audio_log_extended(4u,module,path,function,line,plain); \
 if((audio_log_flags()&1u)||(audio_log_flags()&4u)) \
  (void)compressed_log_output(0x10000000u,compact,compact); \
 break; }
void audio_ble_slave_event_state(uint8_t event) {
 switch(event) {
 EVENT(1u,0x3bu,">>> Reset complete <<<")
 EVENT(3u,0x3fu,">>> Advertising started <<<")
 EVENT(4u,0x43u,">>> Advertising stopped <<<")
 EVENT(5u,0x47u,">>> Scanning started <<<")
 EVENT(6u,0x4bu,">>> Scanning stopped <<<")
 EVENT(7u,0x4fu,">>> Scan data received from peer <<<")
 EVENT(8u,0x53u,">>> Connection opened <<<")
 EVENT(9u,0x57u,">>> Connection closed <<<")
 EVENT(10u,0x5bu,">>> Pairing completed successfully <<<")
 EVENT(11u,0x5fu,">>> Pairing failed <<<")
 EVENT(12u,0x63u,">>> Connection encrypted <<<")
 EVENT(13u,0x67u,">>> Encryption failed <<<")
 EVENT(14u,0x6bu,">>> Prompt user to enter passkey <<<")
 EVENT(18u,0x6fu,">>> Cancel a low or high alert <<<")
 EVENT(19u,0x73u,">>> Low alert <<<")
 EVENT(20u,0x77u,">>> High alert <<<")
 EVENT(21u,0x7bu,">>> Advertising sets started <<<")
 EVENT(22u,0x7fu,">>> Advertising sets stopped <<<")
 EVENT(23u,0x83u,">>> Scan request received <<<")
 EVENT(24u,0x87u,">>> Extended scanning started <<<")
 EVENT(25u,0x8bu,">>> Extended scanning stopped <<<")
 EVENT(26u,0x8fu,">>> Periodic advertising set started <<<")
 EVENT(27u,0x93u,">>> Periodic advertising set stopped <<<")
 EVENT(28u,0x97u,">>> Periodic advertising sync established <<<")
 EVENT(29u,0x9bu,">>> Periodic advertising sync lost <<<")
 EVENT(30u,0x9fu,">>> Periodic APP_UI_HW_ERROR <<<")
 default:break;
 }
 uintptr_t callback=audio_ble_ui_callback_cells[1];
 if(callback)((void (*)(uint8_t,uint32_t))callback)(event,0u);
}
