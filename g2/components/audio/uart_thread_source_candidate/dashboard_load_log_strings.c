/* Native dashboard_ext_load_layout_pb_file (0x501d5c) ROM literals.
 * Pointer cells 0x5025e8..0x502674 identify these exact bytes. */
const char audio_uart_dashboard_path[]="/configure/dashboard_ext.proto";
const char audio_uart_dashboard_mode[]="rb";
const char audio_uart_dashboard_module[]="dashboard.ext";
const char audio_uart_dashboard_source[]=
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\dashboard\\dashboard_ext.c";
const char audio_uart_dashboard_function[]="dashboard_ext_load_layout_pb_file";
const char audio_uart_dashboard_none[]="(none)";

const char audio_uart_dashboard_e_absent[]="layout pb file not exists, skip load: %s";
const char audio_uart_dashboard_c_absent[]="[dashboard.ext]layout pb file not exists, skip load: %s";
const char audio_uart_dashboard_e_open[]="fopen failed: %s";
const char audio_uart_dashboard_c_open[]="[dashboard.ext]fopen failed: %s";
const char audio_uart_dashboard_e_seek_end[]="fseek SEEK_END failed";
const char audio_uart_dashboard_c_seek_end[]="[dashboard.ext]fseek SEEK_END failed";
const char audio_uart_dashboard_e_size[]="invalid layout file size: %ld (max %u)";
const char audio_uart_dashboard_c_size[]="[dashboard.ext]invalid layout file size: %ld (max %u)";
const char audio_uart_dashboard_e_seek_set[]="fseek SEEK_SET failed";
const char audio_uart_dashboard_c_seek_set[]="[dashboard.ext]fseek SEEK_SET failed";
const char audio_uart_dashboard_e_read[]="fread short: expect %ld got %u";
const char audio_uart_dashboard_c_read[]="[dashboard.ext]fread short: expect %ld got %u";
const char audio_uart_dashboard_e_decode[]="DashboardExtLayoutConfigureFile decode failed: %s";
const char audio_uart_dashboard_c_decode[]="[dashboard.ext]DashboardExtLayoutConfigureFile decode failed: %s";
const char audio_uart_dashboard_e_success[]=
    "layout pb loaded: pos=%d widget_count=%u widget_seq_count=%u version='%s' hash='%s'";
const char audio_uart_dashboard_c_success[]=
    "[dashboard.ext]layout pb loaded: pos=%d widget_count=%u widget_seq_count=%u version='%s' hash='%s'";
