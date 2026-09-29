
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_005b38ee(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined *param_4)

{
  undefined1 *puVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uStack_10;
  undefined4 uStack_c;
  
  puVar1 = DAT_005b3e48;
  iVar2 = FUN_005b3628(DAT_005b3e48,param_1);
  uStack_10 = param_3;
  uStack_c = param_4;
  if ((iVar2 == 0) || (*puVar1 = 0, *DAT_005b3e34 != '\x01')) goto LAB_005b39b2;
  if (*_DAT_005b3e74 != '\x01') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uStack_c = PTR_s_loading_timeout__app_not_started_005b3e84;
      uStack_10 = 0xfe;
      FUN_0043d574(2,DAT_005b3e18,DAT_005b3e14,PTR_s_conversate_timer_process_loading_005b3e7c);
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1f < 0) {
LAB_005b399c:
      compress_log_output(0x8000000,PTR_s__conversate_timer_loading_timeou_005b3e88,
                          PTR_s__conversate_timer_loading_timeou_005b3e88);
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1d < 0) goto LAB_005b399c;
    }
    conversate_ui_send_start_request();
    FUN_005b3766();
    goto LAB_005b39b2;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uStack_c = PTR_s_Loading_timeout__enter_main_005b3e78;
    uStack_10 = 0xf9;
    FUN_0043d574(3,DAT_005b3e18,DAT_005b3e14,PTR_s_conversate_timer_process_loading_005b3e7c);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_005b394c:
    compress_log_output(0xc000000,PTR_s__conversate_timer_Loading_timeou_005b3e80,
                        PTR_s__conversate_timer_Loading_timeou_005b3e80);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_005b394c;
  }
  uVar3 = service_time_current_epoch_get();
  FUN_005b02e4(4,uVar3);
LAB_005b39b2:
  return CONCAT44(uStack_c,uStack_10);
}

