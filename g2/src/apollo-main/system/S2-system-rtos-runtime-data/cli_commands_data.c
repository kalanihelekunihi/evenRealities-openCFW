/* FreeRTOS-Plus-CLI command descriptors (CLI_Command_Definition_t) of the
 * Apollo main shell, stock initialised .data 0x200030e4..0x20003663.
 *
 * Evidence: every row is decoded from the startup init image (record
 * 0x75d3f4, LZ-decoded to RAM 0x20000000..0x20004557): +0 command string,
 * +4 help string (both ROM, bytes copied verbatim below), +8 interpreter,
 * +12 int8 expected parameter count (-1 = variable), +13..+15 zero padding.
 * Interpreters are resolved by address to the linked g2/src definitions.
 * The neighbouring .data cells of the same region (cwd 0x200031b4, XIP
 * sector 0x20003324, terminal long query 0x20003630, translate sentences
 * 0x200035e8/0x20003604) are in cli_state_data.c.
 * Strings are placed by the compiler; only the descriptor contents match. */
#include <stddef.h>
#include <stdint.h>

typedef int32_t (*g2_cli_handler_t)(char *write_buffer, size_t write_buffer_len,
                                    const char *command_string);
typedef struct {
    const char *command;          /* +0x0 */
    const char *help;             /* +0x4 */
    g2_cli_handler_t interpreter; /* +0x8 */
    int8_t expected_parameters;   /* +0xc, -1 = variable */
} g2_cli_command_t;
_Static_assert(sizeof(g2_cli_command_t) == 16u, "CLI_Command_Definition_t");

int32_t cli_cmd_ble_get_mac_581150(char *, size_t, const char *); /* 0x581150 */
int32_t cli_cmd_ble_clean_bond_581180(char *, size_t, const char *); /* 0x581180 */
int32_t cli_cmd_ble_slave_58118a(char *, size_t, const char *); /* 0x58118a */
int32_t cli_cmd_ble_master_58125e(char *, size_t, const char *); /* 0x58125e */
int32_t cli_cmd_ble_master_conn_58136c(char *, size_t, const char *); /* 0x58136c */
int32_t cli_cmd_ble_ring_send_5814d4(char *, size_t, const char *); /* 0x5814d4 */
int32_t cli_cmd_em9305_force_dfu_581552(char *, size_t, const char *); /* 0x581552 */
int32_t cli_cmd_ble_adv_581564(char *, size_t, const char *); /* 0x581564 */
int32_t cli_cmd_ble_keep_connect_581628(char *, size_t, const char *); /* 0x581628 */
int32_t cli_cmd_box_force_out_584128(char *, size_t, const char *); /* 0x584128 */
int32_t cli_cmd_buzzer_583df8(char *, size_t, const char *); /* 0x583df8 */
int32_t cli_cmd_audm_580c7c(char *, size_t, const char *); /* 0x580c7c */
int32_t cli_cmd_codec_580d18(char *, size_t, const char *); /* 0x580d18 */
int32_t prvCommand_ls_57e898(char *, size_t, const char *); /* 0x57e898 */
int32_t prvCommand_cat_57e920(char *, size_t, const char *); /* 0x57e920 */
int32_t prvCommand_rm_57ea0a(char *, size_t, const char *); /* 0x57ea0a */
int32_t prvCommand_cd_57eb94(char *, size_t, const char *); /* 0x57eb94 */
int32_t prvCommand_mkdir_57ec7c(char *, size_t, const char *); /* 0x57ec7c */
int32_t prvCommand_touch_57ed26(char *, size_t, const char *); /* 0x57ed26 */
int32_t prvCommand_pwd_57ede2(char *, size_t, const char *); /* 0x57ede2 */
int32_t prvCommand_mv_57ee0c(char *, size_t, const char *); /* 0x57ee0c */
int32_t prvCommand_md5_57f274(char *, size_t, const char *); /* 0x57f274 */
int32_t prvCommand_df_57f3cc(char *, size_t, const char *); /* 0x57f3cc */
int32_t cli_cmd_free_57f550(char *, size_t, const char *); /* 0x57f550 */
int32_t cli_cmd_rename_57f68c(char *, size_t, const char *); /* 0x57f68c */
int32_t cli_cmd_xip_57f8bc(char *, size_t, const char *); /* 0x57f8bc */
int32_t cli_cmd_file2xip_57f980(char *, size_t, const char *); /* 0x57f980 */
int32_t cli_cmd_xip2file_57fcac(char *, size_t, const char *); /* 0x57fcac */
int32_t cli_cmd_gpio_58402a(char *, size_t, const char *); /* 0x58402a */
int32_t cli_cmd_reset_57e3d8(char *, size_t, const char *); /* 0x57e3d8 */
int32_t cli_cmd_clear_57e3e6(char *, size_t, const char *); /* 0x57e3e6 */
int32_t cli_cmd_enter_product_mode_57e3f4(char *, size_t, const char *); /* 0x57e3f4 */
int32_t cli_cmd_exit_product_mode_57e40a(char *, size_t, const char *); /* 0x57e40a */
int32_t cli_cmd_set_gpio_57e420(char *, size_t, const char *); /* 0x57e420 */
int32_t cli_cmd_reset_gpio_57e48e(char *, size_t, const char *); /* 0x57e48e */
int32_t cli_cmd_product_control_codec_57e4fc(char *, size_t, const char *); /* 0x57e4fc */
int32_t cli_cmd_charger_control_57e55a(char *, size_t, const char *); /* 0x57e55a */
int32_t cli_cmd_read_die_id_57e5b6(char *, size_t, const char *); /* 0x57e5b6 */
int32_t cli_cmd_read_chip_id_57e602(char *, size_t, const char *); /* 0x57e602 */
int32_t cli_cmd_info_57e764(char *, size_t, const char *); /* 0x57e764 */
int32_t cli_cmd_at_thread_57e7f6(char *, size_t, const char *); /* 0x57e7f6 */
int32_t cli_cmd_at_dump_57e800(char *, size_t, const char *); /* 0x57e800 */
int32_t cli_cmd_alert_58185c(char *, size_t, const char *); /* 0x58185c */
int32_t cli_cmd_dashboard_layout_581874(char *, size_t, const char *); /* 0x581874 */
int32_t cli_cmd_logcat_580430(char *, size_t, const char *); /* 0x580430 */
int32_t cli_cmd_logf_5804c0(char *, size_t, const char *); /* 0x5804c0 */
int32_t cli_cmd_at_logtype_580518(char *, size_t, const char *); /* 0x580518 */
int32_t cli_cmd_set_language_58421c(char *, size_t, const char *); /* 0x58421c */
int32_t cli_cmd_at_psn_58109c(char *, size_t, const char *); /* 0x58109c */
int32_t cli_cmd_onboarding_58435c(char *, size_t, const char *); /* 0x58435c */
int32_t cli_cmd_pdm_5810f0(char *, size_t, const char *); /* 0x5810f0 */
int32_t cli_cmd_imu_580824(char *, size_t, const char *); /* 0x580824 */
int32_t cli_cmd_set_583918(char *, size_t, const char *); /* 0x583918 */
int32_t cli_cmd_get_5844fe(char *, size_t, const char *); /* 0x5844fe */
int32_t cli_cmd_disp_start_580256(char *, size_t, const char *); /* 0x580256 */
int32_t cli_cmd_single_start_580276(char *, size_t, const char *); /* 0x580276 */
int32_t cli_cmd_single_reflash_580292(char *, size_t, const char *); /* 0x580292 */
int32_t cli_cmd_single_stop_580376(char *, size_t, const char *); /* 0x580376 */
int32_t cli_cmd_disp_stop_5802fe(char *, size_t, const char *); /* 0x5802fe */
int32_t cli_cmd_disp_exit_58031e(char *, size_t, const char *); /* 0x58031e */
int32_t cli_cmd_disp_block_en_58032a(char *, size_t, const char *); /* 0x58032a */
int32_t cli_cmd_disp_block_cancel_58035e(char *, size_t, const char *); /* 0x58035e */
int32_t cli_cmd_input_580100(char *, size_t, const char *); /* 0x580100 */
int32_t cli_cmd_sinput_580144(char *, size_t, const char *); /* 0x580144 */
int32_t cli_cmd_udata_5801b4(char *, size_t, const char *); /* 0x5801b4 */
int32_t cli_cmd_sync_test_5801ee(char *, size_t, const char *); /* 0x5801ee */
int32_t cli_cmd_pdata_58021c(char *, size_t, const char *); /* 0x58021c */
int32_t cli_cmd_disp_reflash_5802c6(char *, size_t, const char *); /* 0x5802c6 */
int32_t cli_cmd_teleprompt_582448(char *, size_t, const char *); /* 0x582448 */
int32_t cli_cmd_translate_5822e6(char *, size_t, const char *); /* 0x5822e6 */
int32_t cli_cmd_conversate_581ed0(char *, size_t, const char *); /* 0x581ed0 */
int32_t cli_cmd_legalregulatory_5827b6(char *, size_t, const char *); /* 0x5827b6 */
int32_t cli_terminal_command_582b0c(char *, size_t, const char *); /* 0x582b0c */
int32_t cli_cmd_tp_581a40(char *, size_t, const char *); /* 0x581a40 */
int32_t cli_cmd_weardetect_581d08(char *, size_t, const char *); /* 0x581d08 */
int32_t cli_cmd_xmodem_581774(char *, size_t, const char *); /* 0x581774 */

/* RAM 0x200030e4; command ROM 0x7880e0, help ROM 0x758280 */
g2_cli_command_t g2_cli_cmd_ble_get_mac_200030e4 __attribute__((aligned(4))) = {
    "AT^BleGetMac",
    "\r\n"
    "AT^BleGetMac:\r\n"
    " get device MAC\r\n",
    cli_cmd_ble_get_mac_581150, 0};
/* RAM 0x200030f4; command ROM 0x7880f0, help ROM 0x736ca4 */
g2_cli_command_t g2_cli_cmd_ble_clean_bond_200030f4 __attribute__((aligned(4))) = {
    "AT^BLECleanBond",
    "\r\n"
    "AT^BLECleanBond:\r\n"
    " BLE Clear Bonding Info\r\n",
    cli_cmd_ble_clean_bond_581180, 0};
/* RAM 0x20003104; command ROM 0x78dfe4, help ROM 0x6d44b4 */
g2_cli_command_t g2_cli_cmd_ble_slave_20003104 __attribute__((aligned(4))) = {
    "AT^BLES",
    "\r\n"
    "AT^BLES [Bondable/Disbondable/DISCONN/RESET9305/HOSTRESET]:\r\n"
    " BLE can bondable or not or slave disconnect or reset 9305 or host reset"
    "\r\n",
    cli_cmd_ble_slave_58118a, 1};
/* RAM 0x20003114; command ROM 0x78dfec, help ROM 0x6db54c */
g2_cli_command_t g2_cli_cmd_ble_master_20003114 __attribute__((aligned(4))) = {
    "AT^BLEM",
    "\r\n"
    "AT^BLEM [Scan/DisScan/RINGSTATE]:\r\n"
    " BLE as master scan other device or not or get ring state\r\n",
    cli_cmd_ble_master_58125e, 1};
/* RAM 0x20003124; command ROM 0x78b840, help ROM 0x6d67b8 */
g2_cli_command_t g2_cli_cmd_ble_master_conn_20003124 __attribute__((aligned(4))) = {
    "AT^BLEMC",
    "\r\n"
    "AT^BLEMC [Conn/Disc] [addr[5]:addr[4]:addr[3]:addr[2]:addr[1]:addr[0]]:\r"
    "\n"
    " BLE as master connect other device or not\r\n",
    cli_cmd_ble_master_conn_58136c, 2};
/* RAM 0x20003134; command ROM 0x788100, help ROM 0x741acc */
g2_cli_command_t g2_cli_cmd_ble_ring_send_20003134 __attribute__((aligned(4))) = {
    "AT^BLERingSend",
    "\r\n"
    "AT^BLERingSend:\r\n"
    " BLE send data to ring\r\n",
    cli_cmd_ble_ring_send_5814d4, 1};
/* RAM 0x20003144; command ROM 0x78b84c, help ROM 0x736cd4 */
g2_cli_command_t g2_cli_cmd_em9305_20003144 __attribute__((aligned(4))) = {
    "AT^EM9305",
    "\r\n"
    "AT^EM9305:\r\n"
    " Force update em9305 firmware\r\n",
    cli_cmd_em9305_force_dfu_581552, 0};
/* RAM 0x20003154; command ROM 0x78b858, help ROM 0x6f5574 */
g2_cli_command_t g2_cli_cmd_ble_adv_20003154 __attribute__((aligned(4))) = {
    "AT^BLEADV",
    "\r\n"
    "AT^BLEADV [START/STOP/STATE]:\r\n"
    " BLE adv start or stop or get adv state\r\n",
    cli_cmd_ble_adv_581564, 1};
/* RAM 0x20003164; command ROM 0x782664, help ROM 0x721908 */
g2_cli_command_t g2_cli_cmd_ble_keep_connect_20003164 __attribute__((aligned(4))) = {
    "AT^BLE_KEEPCONNECT",
    "\r\n"
    "AT^BLE_KEEPCONNECT:\r\n"
    " BLE do not disconnect by self\r\n",
    cli_cmd_ble_keep_connect_581628, 0};
/* RAM 0x20003174; command ROM 0x788130, help ROM 0x6e940c */
g2_cli_command_t g2_cli_cmd_box_force_out_20003174 __attribute__((aligned(4))) = {
    "box_force_out",
    "\r\n"
    "box_force_out <set|clear|status>:\r\n"
    " Force box detect out-of-box state for debug\r\n",
    cli_cmd_box_force_out_584128, 1};
/* RAM 0x20003184; command ROM 0x78e064, help ROM 0x6bf520 */
g2_cli_command_t g2_cli_cmd_buzzer_20003184 __attribute__((aligned(4))) = {
    "buzzer",
    "\r\n"
    "buzzer <subcommand>:\r\n"
    "  note <note> <tone> <beat>: Play buzzer note directly\r\n"
    "    note: 1-7 (do,re,mi,fa,sol,la,si), 0 for silence\r\n"
    "    tone: 0-low, 1-middle, 2-high, 3-super high\r\n"
    "    beat: 1/4 beat unit, larger value means longer duration\r\n"
    "    Example: buzzer note 1 1 2 (middle do, 2 beats)\r\n"
    "  play <type>: Play buzzer type\r\n"
    "    type: 0-touch key, 1-clock alarm, 2-phone call, 3-test1, 4-test2, 5-"
    "single click, 6-double click, 7-long press, 8-swipe left, 9-swipe right,"
    " 10-wear\r\n"
    "    Example: buzzer play 0 (touch key)\r\n",
    cli_cmd_buzzer_583df8, -1};
/* RAM 0x20003194; command ROM 0x78e08c, help ROM 0x6e9460 */
g2_cli_command_t g2_cli_cmd_audm_20003194 __attribute__((aligned(4))) = {
    "audm",
    "\r\n"
    " audm acquire <app_id>: acquire audio\r\n"
    " audm release <app_id>: release audio\r\n",
    cli_cmd_audm_580c7c, -1};
/* RAM 0x200031a4; command ROM 0x78e094, help ROM 0x6d1b2c */
g2_cli_command_t g2_cli_cmd_codec_200031a4 __attribute__((aligned(4))) = {
    "codec",
    "\r\n"
    "codec xxx:\r\n"
    " dfu: update firmware for 8002\r\n"
    " open: open 8002\r\n"
    " close: close 8002\r\n"
    " mic state: query mic state\r\n"
    " mic gain <0-48>: set mic gain\r\n"
    " dmic on|off: enable or disable DMIC\r\n",
    cli_cmd_codec_580d18, -1};
/* RAM 0x20003234; command ROM 0x78f330, help ROM 0x758334 */
g2_cli_command_t g2_cli_cmd_ls_20003234 __attribute__((aligned(4))) = {
    "ls",
    "\r\n"
    "ls:\r\n"
    " list current path file\r\n",
    prvCommand_ls_57e898, 0};
/* RAM 0x20003244; command ROM 0x78f334, help ROM 0x763bf0 */
g2_cli_command_t g2_cli_cmd_cat_20003244 __attribute__((aligned(4))) = {
    "cat",
    "\r\n"
    "cat:\r\n"
    " print file content\r\n",
    prvCommand_cat_57e920, 1};
/* RAM 0x20003254; command ROM 0x78f338, help ROM 0x74cb0c */
g2_cli_command_t g2_cli_cmd_rm_20003254 __attribute__((aligned(4))) = {
    "rm",
    "\r\n"
    "rm:\r\n"
    " Removes a file or directory\r\n",
    prvCommand_rm_57ea0a, 1};
/* RAM 0x20003264; command ROM 0x78f33c, help ROM 0x76fda0 */
g2_cli_command_t g2_cli_cmd_cd_20003264 __attribute__((aligned(4))) = {
    "cd",
    "\r\n"
    "cd:\r\n"
    " open directory\r\n",
    prvCommand_cd_57eb94, 1};
/* RAM 0x20003274; command ROM 0x78e114, help ROM 0x763c10 */
g2_cli_command_t g2_cli_cmd_mkdir_20003274 __attribute__((aligned(4))) = {
    "mkdir",
    "\r\n"
    "mkdir:\r\n"
    " create directory\r\n",
    prvCommand_mkdir_57ec7c, 1};
/* RAM 0x20003284; command ROM 0x78e11c, help ROM 0x76fdbc */
g2_cli_command_t g2_cli_cmd_touch_20003284 __attribute__((aligned(4))) = {
    "touch",
    "\r\n"
    "touch:\r\n"
    " create file\r\n",
    prvCommand_touch_57ed26, 1};
/* RAM 0x20003294; command ROM 0x78f340, help ROM 0x741b50 */
g2_cli_command_t g2_cli_cmd_pwd_20003294 __attribute__((aligned(4))) = {
    "pwd",
    "\r\n"
    "pwd:\r\n"
    " print current working directory\r\n",
    prvCommand_pwd_57ede2, 0};
/* RAM 0x200032a4; command ROM 0x78f344, help ROM 0x74cb34 */
g2_cli_command_t g2_cli_cmd_mv_200032a4 __attribute__((aligned(4))) = {
    "mv",
    "\r\n"
    "mv:\r\n"
    " move/rename file or directory\r\n",
    prvCommand_mv_57ee0c, 2};
/* RAM 0x200032b4; command ROM 0x78f348, help ROM 0x74cb5c */
g2_cli_command_t g2_cli_cmd_md5_200032b4 __attribute__((aligned(4))) = {
    "md5",
    "\r\n"
    "md5:\r\n"
    " calculate MD5 hash of file\r\n",
    prvCommand_md5_57f274, 1};
/* RAM 0x200032c4; command ROM 0x78f34c, help ROM 0x736d04 */
g2_cli_command_t g2_cli_cmd_df_200032c4 __attribute__((aligned(4))) = {
    "df",
    "\r\n"
    "df:\r\n"
    " display filesystem disk space usage\r\n",
    prvCommand_df_57f3cc, 0};
/* RAM 0x200032d4; command ROM 0x78e124, help ROM 0x74cb84 */
g2_cli_command_t g2_cli_cmd_free_200032d4 __attribute__((aligned(4))) = {
    "free",
    "\r\n"
    "free:\r\n"
    " display TLSF memory usage\r\n",
    cli_cmd_free_57f550, 0};
/* RAM 0x200032e4; command ROM 0x78e12c, help ROM 0x74cbac */
g2_cli_command_t g2_cli_cmd_rename_200032e4 __attribute__((aligned(4))) = {
    "rename",
    "\r\n"
    "rename:\r\n"
    " rename file or directory\r\n",
    cli_cmd_rename_57f68c, 2};
/* RAM 0x200032f4; command ROM 0x78f350, help ROM 0x758358 */
g2_cli_command_t g2_cli_cmd_xip_200032f4 __attribute__((aligned(4))) = {
    "xip",
    "\r\n"
    "xip:\r\n"
    " xip address byte-length\r\n",
    cli_cmd_xip_57f8bc, 2};
/* RAM 0x20003304; command ROM 0x78b8f4, help ROM 0x6db614 */
g2_cli_command_t g2_cli_cmd_file2xip_20003304 __attribute__((aligned(4))) = {
    "file2xip",
    "\r\n"
    "file2xip:\r\n"
    " file2xip <filepath> <xip_address>\r\n"
    " Write file to XIP flash at specified address\r\n",
    cli_cmd_file2xip_57f980, 2};
/* RAM 0x20003314; command ROM 0x78b900, help ROM 0x6de3d4 */
g2_cli_command_t g2_cli_cmd_xip2file_20003314 __attribute__((aligned(4))) = {
    "xip2file",
    "\r\n"
    "xip2file:\r\n"
    " xip2file <filepath> <xip_address> <length>\r\n"
    " Read data from XIP address to file\r\n",
    cli_cmd_xip2file_57fcac, 3};
/* RAM 0x20003328; command ROM 0x78e15c, help ROM 0x736f14 */
g2_cli_command_t g2_cli_cmd_gpio_20003328 __attribute__((aligned(4))) = {
    "gpio",
    "\r\n"
    "gpio [num] [level]:\r\n"
    "  level: 0|1|low|high\r\n",
    cli_cmd_gpio_58402a, 2};
/* RAM 0x20003338; command ROM 0x78e16c, help ROM 0x75852c */
g2_cli_command_t g2_cli_cmd_reset_20003338 __attribute__((aligned(4))) = {
    "reset",
    "\r\n"
    "reset:\r\n"
    " software reset system\r\n",
    cli_cmd_reset_57e3d8, 0};
/* RAM 0x20003348; command ROM 0x78e174, help ROM 0x763df0 */
g2_cli_command_t g2_cli_cmd_clear_20003348 __attribute__((aligned(4))) = {
    "clear",
    "\r\n"
    "clear:\r\n"
    " Clear the screen\r\n",
    cli_cmd_clear_57e3e6, 0};
/* RAM 0x20003358; command ROM 0x7827b8, help ROM 0x741cdc */
g2_cli_command_t g2_cli_cmd_enter_product_mode_20003358 __attribute__((aligned(4))) = {
    "enterProductMode",
    "\r\n"
    "enterProductMode:\r\n"
    " Enter product mode\r\n",
    cli_cmd_enter_product_mode_57e3f4, 0};
/* RAM 0x20003368; command ROM 0x788180, help ROM 0x741d08 */
g2_cli_command_t g2_cli_cmd_exit_product_mode_20003368 __attribute__((aligned(4))) = {
    "exitProductMode",
    "\r\n"
    "exitProductMode:\r\n"
    " Exit product mode\r\n",
    cli_cmd_exit_product_mode_57e40a, 0};
/* RAM 0x20003378; command ROM 0x78e17c, help ROM 0x736f44 */
g2_cli_command_t g2_cli_cmd_set_gpio_20003378 __attribute__((aligned(4))) = {
    "SetGPIO",
    "\r\n"
    "SetGPIO <pin>:\r\n"
    " Set GPIO pin to high level\r\n",
    cli_cmd_set_gpio_57e420, 1};
/* RAM 0x20003388; command ROM 0x78b930, help ROM 0x72c138 */
g2_cli_command_t g2_cli_cmd_reset_gpio_20003388 __attribute__((aligned(4))) = {
    "ResetGPIO",
    "\r\n"
    "ResetGPIO <pin>:\r\n"
    " Set GPIO pin to low level\r\n",
    cli_cmd_reset_gpio_57e48e, 1};
/* RAM 0x20003398; command ROM 0x7827cc, help ROM 0x717c44 */
g2_cli_command_t g2_cli_cmd_product_control_codec_20003398 __attribute__((aligned(4))) = {
    "ProductControlCodec",
    "\r\n"
    "ProductControlCodec <on|off>:\r\n"
    " Product control codec\r\n",
    cli_cmd_product_control_codec_57e4fc, 1};
/* RAM 0x200033a8; command ROM 0x788190, help ROM 0x7219e8 */
g2_cli_command_t g2_cli_cmd_charger_control_200033a8 __attribute__((aligned(4))) = {
    "ChargerControl",
    "\r\n"
    "ChargerControl <enable|disable>:\r\n"
    " Charger control\r\n",
    cli_cmd_charger_control_57e55a, 1};
/* RAM 0x200033b8; command ROM 0x78b93c, help ROM 0x763e10 */
g2_cli_command_t g2_cli_cmd_read_die_id_200033b8 __attribute__((aligned(4))) = {
    "ReadDieId",
    "\r\n"
    "ReadDieId:\r\n"
    " Read die id\r\n",
    cli_cmd_read_die_id_57e5b6, 0};
/* RAM 0x200033c8; command ROM 0x78b948, help ROM 0x763e30 */
g2_cli_command_t g2_cli_cmd_read_chip_id_200033c8 __attribute__((aligned(4))) = {
    "ReadChipId",
    "\r\n"
    "ReadChipId:\r\n"
    " Read chip id\r\n",
    cli_cmd_read_chip_id_57e602, 0};
/* RAM 0x200033d8; command ROM 0x78e194, help ROM 0x74ce04 */
g2_cli_command_t g2_cli_cmd_info_200033d8 __attribute__((aligned(4))) = {
    "info",
    "\r\n"
    "info:\r\n"
    " Print product information\r\n",
    cli_cmd_info_57e764, 0};
/* RAM 0x200033e8; command ROM 0x78b960, help ROM 0x74ce2c */
g2_cli_command_t g2_cli_cmd_at_thread_200033e8 __attribute__((aligned(4))) = {
    "AT^thread",
    "\r\n"
    "info:\r\n"
    " Print thread information\r\n",
    cli_cmd_at_thread_57e7f6, 0};
/* RAM 0x200033f8; command ROM 0x78e19c, help ROM 0x758574 */
g2_cli_command_t g2_cli_cmd_at_dump_200033f8 __attribute__((aligned(4))) = {
    "AT^dump",
    "\r\n"
    "info:\r\n"
    " The system will dump\r\n",
    cli_cmd_at_dump_57e800, 0};
/* RAM 0x20003408; command ROM 0x78e1e4, help ROM 0x77aad4 */
g2_cli_command_t g2_cli_cmd_alert_20003408 __attribute__((aligned(4))) = {
    "alert",
    "\r\n"
    "scroll :\r\n"
    " scroll 1\r\n",
    cli_cmd_alert_58185c, 1};
/* RAM 0x20003418; command ROM 0x7827f4, help ROM 0x6d0ecc */
g2_cli_command_t g2_cli_cmd_dashboard_layout_20003418 __attribute__((aligned(4))) = {
    "dashboard_layout",
    "\r\n"
    "dashboard_layout <base_pos> <widget_count> [w0..w4]:\r\n"
    "  base_pos: 0=LEFT 1=CENTER 2=RIGHT\r\n"
    "  widget_count: 0..5\r\n"
    "  wN: 0=SCHEDULE 1=NEWS 2=STOCK 3=HEALTH 4=QUICKLIST\r\n"
    "  takes effect on next dashboard entry\r\n",
    cli_cmd_dashboard_layout_581874, -1};
/* RAM 0x20003428; command ROM 0x78e1ec, help ROM 0x741d60 */
g2_cli_command_t g2_cli_cmd_logcat_20003428 __attribute__((aligned(4))) = {
    "logcat",
    "\r\n"
    "logcat:\r\n"
    " log output level setting .\r\n",
    cli_cmd_logcat_580430, 1};
/* RAM 0x20003438; command ROM 0x78e1f4, help ROM 0x7585e0 */
g2_cli_command_t g2_cli_cmd_logf_20003438 __attribute__((aligned(4))) = {
    "logf",
    "\r\n"
    "logf:\r\n"
    " Use tag tag filtering\r\n",
    cli_cmd_logf_5804c0, 1};
/* RAM 0x20003448; command ROM 0x78b99c, help ROM 0x6ef318 */
g2_cli_command_t g2_cli_cmd_at_logtype_20003448 __attribute__((aligned(4))) = {
    "AT^LOGTYPE",
    "\r\n"
    "AT^LOGTYPE [STORE -d/UART -d/BLE -d/STORE_UART -d]:\r\n"
    " Set compress log type\r\n",
    cli_cmd_at_logtype_580518, 2};
/* RAM 0x20003458; command ROM 0x78b9b4, help ROM 0x72c16c */
g2_cli_command_t g2_cli_cmd_set_language_20003458 __attribute__((aligned(4))) = {
    "SetLanguage",
    "\r\n"
    "SetLanguage:\r\n"
    " en-GB/de/fr/es/it/ja/zh-CN/zh-HK\r\n",
    cli_cmd_set_language_58421c, 1};
/* RAM 0x20003468; command ROM 0x78e234, help ROM 0x763eb0 */
g2_cli_command_t g2_cli_cmd_at_psn_20003468 __attribute__((aligned(4))) = {
    "AT^psn",
    "\r\n"
    "AT^psn XXX:\r\n"
    " set NV PSN\r\n",
    cli_cmd_at_psn_58109c, 1};
/* RAM 0x20003478; command ROM 0x78b9c0, help ROM 0x6d20e0 */
g2_cli_command_t g2_cli_cmd_onboarding_20003478 __attribute__((aligned(4))) = {
    "onboarding",
    "\r\n"
    "onboarding:\r\n"
    " Manage onboarding flag\r\n"
    "  onboarding getFlag      - Query onboarding flag value\r\n"
    "  onboarding setFlag <0|1> - Set onboarding flag (e.g., onboarding setFl"
    "ag 1)\r\n",
    cli_cmd_onboarding_58435c, -1};
/* RAM 0x20003488; command ROM 0x78f354, help ROM 0x736fa4 */
g2_cli_command_t g2_cli_cmd_pdm_20003488 __attribute__((aligned(4))) = {
    "pdm",
    "\r\n"
    "pdm [open|close]\r\n"
    " start or stop pdm test\r\n",
    cli_cmd_pdm_5810f0, 1};
/* RAM 0x20003498; command ROM 0x78f358, help ROM 0x6bf308 */
g2_cli_command_t g2_cli_cmd_imu_20003498 __attribute__((aligned(4))) = {
    "imu",
    "\r\n"
    "imu [open|close|rawdata|rnv|wnv|mode|calib]:\r\n"
    "  open                    - Start IMU sensor test mode\r\n"
    "  close                     - Stop IMU sensor test mode\r\n"
    "  rawdata <1|0>            - Start/stop raw data collection to CSV\r\n"
    "  rnv <acc|gyr|matrix>     - Read sensor calibration data\r\n"
    "  wnv <acc|gyr|matrix> <x> <y> <z> - Write sensor calibration data\r\n"
    "  mode <0-4>               - Set IMU work mode\r\n"
    "  calib update             - Update calibration parameters\r\n"
    "  acc <1|0> <interval>   - Start/stop accelerometer data collection\r\n",
    cli_cmd_imu_580824, -1};
/* RAM 0x200034a8; command ROM 0x78f35c, help ROM 0x6a199c */
g2_cli_command_t g2_cli_cmd_set_200034a8 __attribute__((aligned(4))) = {
    "set",
    "\r\n"
    "set:\r\n"
    " Set the system setting\r\n"
    "  set screen height <value>  - Set screen height (e.g., set screen heigh"
    "t 32)\r\n",
    cli_cmd_set_583918, -1};
/* RAM 0x200034b8; command ROM 0x78f360, help ROM 0x6c0d50 */
g2_cli_command_t g2_cli_cmd_get_200034b8 __attribute__((aligned(4))) = {
    "get",
    "\r\n"
    "get:\r\n"
    " Get the system setting value\r\n"
    "  get time_format        - Get time format (0:24H, 1:12H)\r\n"
    "  get temperature_unit   - Get temperature unit (1:\302\260C, 2:\302\260"
    "F)\r\n"
    "  get date_format        - Get date format (0:YYYY/MM/DD, 1:MM/DD/YYYY, "
    "2:DD/MM/YYYY)\r\n"
    "  get distance_unit      - Get distance unit (0:km, 1:mi)\r\n"
    "  get metric_unit        - Get metric unit (0:metric, 1:imperial)\r\n"
    "  get dominant_hand      - Get dominant hand (0:left, 1:right)\r\n"
    "  get gesture_app        - Get gesture app settings\r\n",
    cli_cmd_get_5844fe, -1};
/* RAM 0x200034c8; command ROM 0x78ba44, help ROM 0x6ef368 */
g2_cli_command_t g2_cli_cmd_disp_start_200034c8 __attribute__((aligned(4))) = {
    "dispStart",
    "\r\n"
    "dispStart:\r\n"
    " start up app. ex: dispStart 1 . startup Dashboard application\r\n",
    cli_cmd_disp_start_580256, 1};
/* RAM 0x200034d8; command ROM 0x78ba50, help ROM 0x6e955c */
g2_cli_command_t g2_cli_cmd_single_start_200034d8 __attribute__((aligned(4))) = {
    "singleStart",
    "\r\n"
    "singleStart:\r\n"
    " start up app. ex: singleStart 1 . startup Dashboard application\r\n",
    cli_cmd_single_start_580276, 1};
/* RAM 0x200034e8; command ROM 0x788230, help ROM 0x6e47f8 */
g2_cli_command_t g2_cli_cmd_single_reflash_200034e8 __attribute__((aligned(4))) = {
    "singleReflash",
    "\r\n"
    "singleReflash:\r\n"
    " start up app. ex: singleReflash 1 . reflash Dashboard application\r\n",
    cli_cmd_single_reflash_580292, 2};
/* RAM 0x200034f8; command ROM 0x78ba5c, help ROM 0x6f56f0 */
g2_cli_command_t g2_cli_cmd_single_stop_200034f8 __attribute__((aligned(4))) = {
    "singleStop",
    "\r\n"
    "singleStop:\r\n"
    " close app.ex : singleStop 1 . close Dashboard application\r\n",
    cli_cmd_single_stop_580376, 1};
/* RAM 0x20003508; command ROM 0x78ba68, help ROM 0x6fc1dc */
g2_cli_command_t g2_cli_cmd_disp_stop_20003508 __attribute__((aligned(4))) = {
    "dispStop",
    "\r\n"
    "dispStop:\r\n"
    " close app.ex :dispStop 1 . close Dashboard application\r\n",
    cli_cmd_disp_stop_5802fe, 1};
/* RAM 0x20003518; command ROM 0x78ba74, help ROM 0x72c208 */
g2_cli_command_t g2_cli_cmd_disp_exit_20003518 __attribute__((aligned(4))) = {
    "dispExit",
    "\r\n"
    "dispExit:\r\n"
    " exit all display apps. ex :dispExit\r\n",
    cli_cmd_disp_exit_58031e, 0};
/* RAM 0x20003528; command ROM 0x78ba80, help ROM 0x6e4850 */
g2_cli_command_t g2_cli_cmd_disp_block_en_20003528 __attribute__((aligned(4))) = {
    "dispBlockEn",
    "\r\n"
    "dispBlockEn:\r\n"
    " enable display start blocking. ex: dispBlockEn 1000 (ms, max 5000)\r\n",
    cli_cmd_disp_block_en_58032a, 1};
/* RAM 0x20003538; command ROM 0x788240, help ROM 0x6e48a8 */
g2_cli_command_t g2_cli_cmd_disp_block_cancel_20003538 __attribute__((aligned(4))) = {
    "dispBlockCancel",
    "\r\n"
    "dispBlockCancel:\r\n"
    " cancel display start blocking immediately. ex: dispBlockCancel\r\n",
    cli_cmd_disp_block_cancel_58035e, 0};
/* RAM 0x20003548; command ROM 0x78e2d4, help ROM 0x6f573c */
g2_cli_command_t g2_cli_cmd_input_20003548 __attribute__((aligned(4))) = {
    "input",
    "\r\n"
    "input:\r\n"
    " inject input event. ex :input 0 1 0. inject duoble click event\r\n",
    cli_cmd_input_580100, 3};
/* RAM 0x20003558; command ROM 0x78e2dc, help ROM 0x6db678 */
g2_cli_command_t g2_cli_cmd_sinput_20003558 __attribute__((aligned(4))) = {
    "sinput",
    "\r\n"
    "sinput:\r\n"
    " inject input event to display thread . ex :sinput 0 1 0. inject duoble "
    "click event\r\n",
    cli_cmd_sinput_580144, 3};
/* RAM 0x20003568; command ROM 0x78e2e4, help ROM 0x6db6dc */
g2_cli_command_t g2_cli_cmd_udata_20003568 __attribute__((aligned(4))) = {
    "udata",
    "\r\n"
    "udata:\r\n"
    " send user data to both.ex :udata 1 123 . The Application 1 will receive"
    "d 123 string .\r\n",
    cli_cmd_udata_5801b4, 2};
/* RAM 0x20003578; command ROM 0x78ba8c, help ROM 0x7828d0 */
g2_cli_command_t g2_cli_cmd_sync_test_20003578 __attribute__((aligned(4))) = {
    "syncTest",
    "\r\n"
    "syncTest:\r\n"
    " \r\n",
    cli_cmd_sync_test_5801ee, 1};
/* RAM 0x20003588; command ROM 0x78e2ec, help ROM 0x6d7510 */
g2_cli_command_t g2_cli_cmd_pdata_20003588 __attribute__((aligned(4))) = {
    "pdata",
    "\r\n"
    "pdata:\r\n"
    " send user data to peer.ex :pdata 123 . Master send 123 string.The Salve"
    " will received 123 string.\r\n",
    cli_cmd_pdata_58021c, 2};
/* RAM 0x20003598; command ROM 0x78ba98, help ROM 0x6d9704 */
g2_cli_command_t g2_cli_cmd_disp_reflash_20003598 __attribute__((aligned(4))) = {
    "dispReflash",
    "\r\n"
    "dispReflash:\r\n"
    " send Reflash data to both.ex : dispReflash 1 1 . send Display reflash d"
    "ata to both\r\n",
    cli_cmd_disp_reflash_5802c6, 2};
/* RAM 0x200035a8; command ROM 0x78baa4, help ROM 0x6cb0f4 */
g2_cli_command_t g2_cli_cmd_teleprompt_200035a8 __attribute__((aligned(4))) = {
    "teleprompt",
    "\r\n"
    "teleprompt <sub>:\r\n"
    "  start <start_page> <total_pages> [lines5-9] [scroll 0=cont/1=page/2=of"
    "f] [mode 0=AI/1=MAN/2=AUTO]\r\n"
    "  fill [total_pages] [lines_per_page<=10] - inject fake page text (run a"
    "fter start)\r\n"
    "  pause | resume | stop\r\n"
    "  aisync <page> <line> <char>\r\n"
    "  page <id> - print cached page\r\n",
    cli_cmd_teleprompt_582448, -1};
/* RAM 0x200035b8; command ROM 0x78bab0, help ROM 0x7828e4 */
g2_cli_command_t g2_cli_cmd_translate_200035b8 __attribute__((aligned(4))) = {
    "translate",
    "\r\n"
    "translate xxx:\r\n",
    cli_cmd_translate_5822e6, -1};
/* RAM 0x200035c8; command ROM 0x78babc, help ROM 0x6c88b4 */
g2_cli_command_t g2_cli_cmd_conversate_200035c8 __attribute__((aligned(4))) = {
    "conversate",
    "\r\n"
    "conversate xxx:\r\n"
    "  conversate start [prepnote] - start conversate, optional arg enables b"
    "uilt-in 2-packet prep note\r\n"
    "  conversate packet <0|1> - send built-in prep note packet 0 or 1\r\n"
    "  conversate preplist [count] - inject fake prep note list to machine ha"
    "ndler\r\n"
    "  conversate tag <type> <text> [extend_text] - set tag data\r\n"
    "  conversate cache - print cached data\r\n",
    cli_cmd_conversate_581ed0, -1};
/* RAM 0x200035d8; command ROM 0x788250, help ROM 0x7702c4 */
g2_cli_command_t g2_cli_cmd_legalregulatory_200035d8 __attribute__((aligned(4))) = {
    "legalregulatory",
    "\r\n"
    "legalregulatory xxx:\r\n",
    cli_cmd_legalregulatory_5827b6, -1};
/* RAM 0x20003620; command ROM 0x78baec, help ROM 0x6834a8 */
g2_cli_command_t g2_cli_cmd_terminal_20003620 __attribute__((aligned(4))) = {
    "terminal",
    "\r\n"
    "terminal:\r\n"
    "  terminal mode <0|1>                     - simulate mode sync (0=daily,"
    " 1=terminal)\r\n"
    "  terminal content <hi|dim> <add|rep> <t> - simulate agent content (styl"
    "e + op + text)\r\n"
    "  terminal asr [text]                     - simulate ASR interim chunk ("
    "sentence_final=0 all_final=0)\r\n"
    "  terminal asr_sfinal [text]              - simulate sentence final chun"
    "k (sentence_final=1 all_final=0)\r\n"
    "  terminal asr_final [text]               - simulate all final chunk (se"
    "ntence_final=1 all_final=1)\r\n"
    "  terminal status <0-4>                   - simulate session status (0:n"
    "one 1:thinking 2:await_user 3:done 4:reset)\r\n"
    "  terminal reset                          - simulate session status SESS"
    "ION_STATUS_RESET\r\n"
    "  terminal host <0-2>                     - simulate host status (0:no_h"
    "ost,1:offline,2:streaming)\r\n"
    "  terminal ble <0|1>                      - simulate ble callback (0=dis"
    "connected,1=connected)\r\n"
    "  terminal query <text> <cnt>             - simulate query with option 1"
    "..N\r\n"
    "  terminal query_long                     - simulate long query with 8 o"
    "ptions\r\n"
    "  terminal query_reply <opt> [qid]        - simulate app-side query repl"
    "y (default qid = cached query)\r\n"
    "  terminal err <0-2>                      - simulate error msg (0:succes"
    "s 1:fail 2:asr_failed)\r\n"
    "  terminal session_list <host> <cur> <cnt>- simulate session list, ids a"
    "re 1..cnt\r\n"
    "  terminal switch_result <0|1>             - simulate switch result (0=s"
    "uccess,1=failed)\r\n"
    "  terminal new_result <0|1>                - simulate new session result"
    " (0=success,1=failed)\r\n"
    "  terminal session_changed <id>            - simulate current session id"
    " changed\r\n"
    "  terminal cache                          - print cached data\r\n",
    cli_terminal_command_582b0c, -1};
/* RAM 0x20003634; command ROM 0x78f364, help ROM 0x6c8a24 */
g2_cli_command_t g2_cli_cmd_tp_20003634 __attribute__((aligned(4))) = {
    "tp",
    "\r\n"
    "version : get touch version\r\n"
    " dfu [force] : check/update touch firmware\r\n"
    " reset : reset touch\r\n"
    " diff : read diff once\r\n"
    " diff_always : read diff continuously\r\n"
    " bsln_read : read proximity baseline from EEPROM\r\n"
    " bsln_set : save proximity baseline to EEPROM\r\n"
    " cfg read : read current touch gesture config\r\n"
    " cfg write <threshold_ms> : write touch gesture config\r\n",
    cli_cmd_tp_581a40, -1};
/* RAM 0x20003644; command ROM 0x78bb7c, help ROM 0x7589f4 */
g2_cli_command_t g2_cli_cmd_weardetect_20003644 __attribute__((aligned(4))) = {
    "weardetect",
    "\r\n"
    "weardetect:\r\n"
    " weardetect 0 or 1\r\n",
    cli_cmd_weardetect_581d08, -1};
/* RAM 0x20003654; command ROM 0x78e3d4, help ROM 0x6db740 */
g2_cli_command_t g2_cli_cmd_xmodem_20003654 __attribute__((aligned(4))) = {
    "xmodem",
    "\r\n"
    "xmodem:\r\n"
    " use xmodem protocol receive or send file .ex : xmodem -r file.txt | xmo"
    "de -s file.txt\r\n",
    cli_cmd_xmodem_581774, 2};
