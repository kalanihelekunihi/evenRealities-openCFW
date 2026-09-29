
void FUN_0049c3d8(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_14;
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  if (param_2 == (undefined4 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,PTR_s_dashboard_0049cb30,DAT_0049cb2c,DAT_0049cd48,0xd0,DAT_0049cd44);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0049cd4c);
    }
  }
  else {
    uVar2 = *param_2;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_14 = uVar2;
      FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,DAT_0049cd48,0xd5,DAT_0049cd50,param_1);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_0049cd54,DAT_0049cd54,param_1,uVar2);
    }
    if (param_1 == 0) {
      iVar1 = FUN_0045a568();
      if (((iVar1 == 1) && (iVar1 = FUN_00443484(), iVar1 == 1)) &&
         (iVar1 = FUN_004434d0(1), iVar1 == 1)) {
        local_14._0_2_ = CONCAT11(*DAT_0049cd58,(undefined1)local_14);
        uVar2 = FUN_00464bb2(1,(int)&local_14 + 1,1,0);
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,DAT_0049cd48,0xdd,DAT_0049cd3c,uVar2)
          ;
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0049cd40,DAT_0049cd40,uVar2);
        }
      }
    }
    else if (param_1 == 1) {
      iVar1 = FUN_0045a568();
      if (((iVar1 == 1) && (iVar1 = FUN_00443484(), iVar1 == 1)) &&
         (iVar1 = FUN_004434d0(1), iVar1 == 1)) {
        local_14 = CONCAT31(local_14._1_3_,*DAT_0049cd5c);
        uVar2 = FUN_00464bb2(1,&local_14,1,0);
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(4,PTR_s_dashboard_0049cb30,DAT_0049cb2c,DAT_0049cd48,0xe6,DAT_0049cd3c,uVar2)
          ;
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_0049cd40,DAT_0049cd40,uVar2);
        }
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(2,PTR_s_dashboard_0049cb30,DAT_0049cb2c,DAT_0049cd48,0xeb,DAT_0049cd60,param_1)
        ;
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x8400000,PTR_s__dashboard_Unknown_battery_event_0049cd64,
                            PTR_s__dashboard_Unknown_battery_event_0049cd64,param_1);
      }
    }
  }
  return;
}

