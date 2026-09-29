
void terminal_data_start_response_timer
               (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  
  iVar1 = td_current_record(param_1);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(2,DAT_00597c2c,DAT_00597c28,DAT_00597c3c,0x15f,DAT_00597c38,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_00597c40,DAT_00597c40,param_1);
    }
  }
  else {
    uVar2 = service_time_rtc_refresh();
    *(undefined4 *)(iVar1 + 0x88) = uVar2;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(3,DAT_00597c2c,DAT_00597c28,DAT_00597c3c,0x164,DAT_00597c44,param_1,
                   *(undefined4 *)(iVar1 + 0x88),param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_00597c48,DAT_00597c48,param_1,*(undefined4 *)(iVar1 + 0x88))
      ;
    }
  }
  return;
}

