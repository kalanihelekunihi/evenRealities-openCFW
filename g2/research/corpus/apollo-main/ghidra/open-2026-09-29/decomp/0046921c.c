
void SilentMode_SetStatusFromApp(uint param_1)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uStack_10;
  
  uStack_10 = param_1;
  if (*DAT_00469b44 == '\0') {
    *DAT_00469b54 = 1;
    uVar2 = silent_mode_status_get();
    if (((uStack_10 & 0xff) != 0) && (iVar1 = FUN_00443484(), iVar1 != 0)) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00469b3c,DAT_00469b38,PTR_s_SilentMode_SetStatusFromApp_00469b4c,99,
                     PTR_s_Silent_mode_ON_from_APP__screen_i_00469b58);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc000000,PTR_s__silent_mode_Silent_mode_ON_from_00469b5c);
      }
      iVar1 = FUN_0045a568();
      if (iVar1 == 1) {
        iVar1 = FUN_0044349c();
        if (iVar1 == 1) {
          FUN_00464c36(0,0,0,0);
        }
        iVar3 = FUN_004434b4();
        if (iVar3 == 1) {
          if (iVar1 == 1) {
            FUN_00454b4c(500);
            FUN_00464c36(0,0,0,0);
          }
          else {
            FUN_00464c36(0,0,0,0);
          }
        }
      }
    }
    if (((uVar2 & 0xff) != (uStack_10 & 0xff)) &&
       (iVar1 = FUN_00464f76(0x10a,&uStack_10,1,0,4), iVar1 != 0)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00469b3c,DAT_00469b38,PTR_s_SilentMode_SetStatusFromApp_00469b4c,0x7e,
                     PTR_s_Failed_to_send_data_to_both_ret__00469b60,iVar1);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,PTR_s__silent_mode_Failed_to_send_data_00469b64,
                            PTR_s__silent_mode_Failed_to_send_data_00469b64,iVar1);
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_00469b3c,DAT_00469b38,PTR_s_SilentMode_SetStatusFromApp_00469b4c,0x58,
                   PTR_s_silent_mode_is_showing_ui__not_s_00469b48);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__silent_mode_silent_mode_is_show_00469b50,
                          PTR_s__silent_mode_silent_mode_is_show_00469b50);
    }
  }
  return;
}

