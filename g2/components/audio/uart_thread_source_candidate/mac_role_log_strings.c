/* Apollo ring MAC and role GPIO diagnostics from the official ROM. */
const unsigned int audio_uart_role_pin_config=0x93u;
const char audio_uart_mac_source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
const char audio_uart_mac_module[]="ble.master";
const char audio_uart_mac_function[]="APP_MasterRingMacIsSet";
const char audio_uart_mac_e_hi[]="ringAddr = %02X:%02X:%02X:";
const char audio_uart_mac_c_hi[]="[ble.master]ringAddr = %02X:%02X:%02X:";
const char audio_uart_mac_e_lo[]="ringAddr = %02X:%02X:%02X";
const char audio_uart_mac_c_lo[]="[ble.master]ringAddr = %02X:%02X:%02X";
const char audio_uart_mac_e_absent[]="[Ring] RingMacIsSet: ringMac not set";
const char audio_uart_mac_c_absent[]="[ble.master][Ring] RingMacIsSet: ringMac not set";

const char audio_uart_role_function[]="_private_getCurrentRoleStatus";
const char audio_uart_role_e_unstable[]="GPIO readings inconsistent, retrying...";
const char audio_uart_role_c_unstable[]="[sync.module.framework]GPIO readings inconsistent, retrying...";
const char audio_uart_role_e_stable[]="role IO status = %d (after debounce)";
const char audio_uart_role_c_stable[]="[sync.module.framework]role IO status = %d (after debounce)";
