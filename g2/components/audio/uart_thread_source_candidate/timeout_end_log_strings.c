/* Native sync timeout listener diagnostics and callback names. */
const char audio_uart_timeout_name_peer[]="_PeerData_TimeoutListener";
const char audio_uart_timeout_name_user[]="_UserDataCmd_TimeoutListener";
const char audio_uart_timeout_name_slave[]="_SlaveScheduleModuleDataCmd_TimeoutListener";
const char audio_uart_timeout_name_input[]="_MasterInputEventDataCmd_TimeoutListener";
const char audio_uart_timeout_name_display[]="_MasterDisplayCmd_TimeoutListener";
const char audio_uart_timeout_running_text[]="%s :timeout running";
const char audio_uart_timeout_compact[]="[sync.module.framework]%s :timeout running";
const char audio_uart_timeout_submit_failed[]="submit work failed,";
const char audio_uart_timeout_submit_compact[]="[sync.module.framework]submit work failed,";
