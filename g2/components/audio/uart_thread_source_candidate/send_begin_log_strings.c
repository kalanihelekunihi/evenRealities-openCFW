/* Native Apollo sync_framework.c diagnostic strings for the four
 * _*DataCmd_Listener bodies at 0x45daa0, 0x45d7e4, 0x45dd68, 0x45d554. */
const char audio_uart_begin0_module[]="sync.module.framework";
const char audio_uart_begin0_source[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\framework\\sync\\sync_framework.c";
extern const char audio_uart_begin1_module[sizeof(audio_uart_begin0_module)]
    __attribute__((alias("audio_uart_begin0_module")));
extern const char audio_uart_begin3_module[sizeof(audio_uart_begin0_module)]
    __attribute__((alias("audio_uart_begin0_module")));
extern const char audio_uart_begin4_module[sizeof(audio_uart_begin0_module)]
    __attribute__((alias("audio_uart_begin0_module")));
extern const char audio_uart_begin1_source[sizeof(audio_uart_begin0_source)]
    __attribute__((alias("audio_uart_begin0_source")));
extern const char audio_uart_begin3_source[sizeof(audio_uart_begin0_source)]
    __attribute__((alias("audio_uart_begin0_source")));
extern const char audio_uart_begin4_source[sizeof(audio_uart_begin0_source)]
    __attribute__((alias("audio_uart_begin0_source")));

const char audio_uart_begin0_function[]="_SlaveScheduleModuleDataCmd_Listener";
const char audio_uart_begin1_function[]="_UserDataCmd_Listener";
const char audio_uart_begin3_function[]="_MasterInputEventDataCmd_Listener";
const char audio_uart_begin4_function[]="_PeerData_Listener";

const char audio_uart_begin_e_null[]="msg data is null,timeout resource release";
const char audio_uart_begin_c_null[]=
    "[sync.module.framework]msg data is null,timeout resource release";
const char audio_uart_begin_e_event[]="SyncEventType = %d";
const char audio_uart_begin_c_event[]="[sync.module.framework]SyncEventType = %d";
const char audio_uart_begin_e_userdata[]="userdata is null";
const char audio_uart_begin_c_userdata[]="[sync.module.framework]userdata is null";
const char audio_uart_begin_e_submit[]="submit work failed,";
const char audio_uart_begin_c_submit[]="[sync.module.framework]submit work failed,";

const char audio_uart_begin0_e_received[]="received schedule sync command  response";
const char audio_uart_begin0_c_received[]=
    "[sync.module.framework]received schedule sync command  response";
const char audio_uart_begin1_e_received[]="received user data response";
const char audio_uart_begin1_c_received[]=
    "[sync.module.framework]received user data response";
const char audio_uart_begin3_e_received[]="received input event response";
const char audio_uart_begin3_c_received[]=
    "[sync.module.framework]received input event response";
const char audio_uart_begin4_e_received[]="received peer data response";
const char audio_uart_begin4_c_received[]=
    "[sync.module.framework]received peer data response";
