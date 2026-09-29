
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

longlong FUN_004d3354(int param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  
  if (param_1 == 2) {
    uVar2 = param_3;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar2 = 0x134;
      FUN_0043d574(4,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                   PTR_s_system_alert_ui_event_handler_004d34b0,0x134,
                   PTR_s_system_alert_MainPage_init_004d34ac);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,PTR_s__system_alert_system_alert_MainP_004d34b4,
                          PTR_s__system_alert_system_alert_MainP_004d34b4);
    }
    FUN_004d2f48(param_4,param_2,param_3);
    *(undefined4 *)(_DAT_004d34b8 + 4) = *_DAT_004d3478;
    *_DAT_004d3440 = 1;
    *_DAT_004d3444 = 0xb4;
    param_3 = uVar2;
  }
  else if (param_1 == 3) {
    FUN_004d30ba(param_2,param_3);
  }
  else if ((param_1 != 4) && (param_1 == 5)) {
    *_DAT_004d3440 = 0;
    *_DAT_004d3444 = 0xb4;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x14c;
      FUN_0043d574(3,PTR_s_system_alert_004d3428,PTR_s_D__01_workspace_s200_ap510b_iar__004d3424,
                   PTR_s_system_alert_ui_event_handler_004d34b0,0x14c,_DAT_004d34bc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,_DAT_004d34c0,_DAT_004d34c0);
    }
  }
  return (ulonglong)param_3 << 0x20;
}

