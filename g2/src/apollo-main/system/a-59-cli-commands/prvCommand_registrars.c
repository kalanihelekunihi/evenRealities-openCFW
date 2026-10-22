/* Registrars of the remaining product FreeRTOS-Plus-CLI modules, stock
 * directory D:\01_workspace\s200_ap510b_iar_git\kernel\FreeRTOS-Plus-CLI\
 * prvCommand\. Each function is the tail of its own (unnamed) module and
 * follows that module's handlers, none of which has an inventory row:
 *   display  0x580392..0x5803e9 (pool 0x5803f8..), handlers 0x580100..0x580376
 *   log      0x5807c0..0x5807d5 (pool 0x580818..), handlers 0x580430..0x580518
 *   imu      0x580c04..0x580c0d (pool 0x580c78),   handler  0x580824
 *   audio    0x580fec..0x580ffb (pool 0x581094..), handlers 0x580c7c, 0x580d18
 *   psn      0x5810d8..0x5810e1 (pool 0x5810ec),   handler  0x58109c
 *   pdm      0x581136..0x58113f (pool 0x58114c),   handler  0x5810f0
 *   xmodem   0x58183a..0x581843 (pool 0x581858),   handler  0x581774
 *   ui       0x581960..0x58196f (pool 0x581984..), handlers 0x58185c, 0x581874
 *   touch    0x581d60..0x581d6f (pool 0x581d78, 0x581ddc), handlers 0x581a40, 0x581d08
 * Registration order is the stock call order. */
#include <stdint.h>
#include "cli_commands.h"

extern g2_cli_command_t g2_cli_cmd_sync_test_20003578;        /* "syncTest", 1 param */
extern g2_cli_command_t g2_cli_cmd_input_20003548;            /* "input", 3 */
extern g2_cli_command_t g2_cli_cmd_disp_stop_20003508;        /* "dispStop", 1 */
extern g2_cli_command_t g2_cli_cmd_disp_exit_20003518;        /* "dispExit", 0 */
extern g2_cli_command_t g2_cli_cmd_disp_block_en_20003528;    /* "dispBlockEn", 1 */
extern g2_cli_command_t g2_cli_cmd_disp_block_cancel_20003538; /* "dispBlockCancel", 0 */
extern g2_cli_command_t g2_cli_cmd_disp_start_200034c8;       /* "dispStart", 1 */
extern g2_cli_command_t g2_cli_cmd_udata_20003568;            /* "udata", 2 */
extern g2_cli_command_t g2_cli_cmd_pdata_20003588;            /* "pdata", 2 */
extern g2_cli_command_t g2_cli_cmd_disp_reflash_20003598;     /* "dispReflash", 2 */
extern g2_cli_command_t g2_cli_cmd_single_start_200034d8;     /* "singleStart", 1 */
extern g2_cli_command_t g2_cli_cmd_single_stop_200034f8;      /* "singleStop", 1 */
extern g2_cli_command_t g2_cli_cmd_single_reflash_200034e8;   /* "singleReflash", 2 */
extern g2_cli_command_t g2_cli_cmd_sinput_20003558;           /* "sinput", 3 */
extern g2_cli_command_t g2_cli_cmd_logcat_20003428;           /* "logcat", 1 */
extern g2_cli_command_t g2_cli_cmd_logf_20003438;             /* "logf", 1 */
extern g2_cli_command_t g2_cli_cmd_at_logtype_20003448;       /* "AT^LOGTYPE", 2 */
extern g2_cli_command_t g2_cli_cmd_imu_20003498;              /* "imu", variable */
extern g2_cli_command_t g2_cli_cmd_codec_200031a4;            /* "codec", variable */
extern g2_cli_command_t g2_cli_cmd_audm_20003194;             /* "audm", variable */
extern g2_cli_command_t g2_cli_cmd_at_psn_20003468;           /* "AT^psn", 1 */
extern g2_cli_command_t g2_cli_cmd_pdm_20003488;              /* "pdm", 1 */
extern g2_cli_command_t g2_cli_cmd_xmodem_20003654;           /* "xmodem", 2 */
extern g2_cli_command_t g2_cli_cmd_alert_20003408;            /* "alert", 1 (help text is "scroll") */
extern g2_cli_command_t g2_cli_cmd_dashboard_layout_20003418; /* "dashboard_layout", variable */
extern g2_cli_command_t g2_cli_cmd_tp_20003634;               /* "tp", variable */
extern g2_cli_command_t g2_cli_cmd_weardetect_20003644;       /* "weardetect", variable */

void cli_register_display_commands_580392(void);
void cli_register_log_commands_5807c0(void);
void cli_register_imu_command_580c04(void);
void cli_register_audio_commands_580fec(void);
void cli_register_psn_command_5810d8(void);
void cli_register_pdm_command_581136(void);
void cli_register_xmodem_command_58183a(void);
void cli_register_ui_commands_581960(void);
void cli_register_touch_commands_581d60(void);

void cli_register_display_commands_580392(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_sync_test_20003578);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_input_20003548);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_disp_stop_20003508);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_disp_exit_20003518);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_disp_block_en_20003528);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_disp_block_cancel_20003538);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_disp_start_200034c8);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_udata_20003568);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_pdata_20003588);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_disp_reflash_20003598);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_single_start_200034d8);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_single_stop_200034f8);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_single_reflash_200034e8);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_sinput_20003558);
}

void cli_register_log_commands_5807c0(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_logcat_20003428);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_logf_20003438);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_at_logtype_20003448);
}

void cli_register_imu_command_580c04(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_imu_20003498);
}

void cli_register_audio_commands_580fec(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_codec_200031a4);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_audm_20003194);
}

void cli_register_psn_command_5810d8(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_at_psn_20003468);
}

void cli_register_pdm_command_581136(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_pdm_20003488);
}

void cli_register_xmodem_command_58183a(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_xmodem_20003654);
}

void cli_register_ui_commands_581960(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_alert_20003408);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_dashboard_layout_20003418);
}

void cli_register_touch_commands_581d60(void)
{
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_tp_20003634);
    (void)freertos_cli_register_command_5847ac(&g2_cli_cmd_weardetect_20003644);
}
