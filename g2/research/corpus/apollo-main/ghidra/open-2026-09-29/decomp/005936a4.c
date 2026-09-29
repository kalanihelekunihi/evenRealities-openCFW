
undefined8
am_devices_jbd4010_status_check_and_recovery
          (undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  byte bVar2;
  
  iVar1 = jdb4010_status_check(1);
  if (iVar1 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x336;
      FUN_0043d574(4,DAT_00593900,DAT_005938fc,PTR_s_am_devices_jbd4010_status_check__0059397c,0x336
                   ,PTR_s_jdb4010_status_is_normal_00593984);
    }
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1f < 0) {
LAB_00593720:
      compress_log_output(0x10000000,PTR_s__driver_jbd4010_jdb4010_status_i_00593988,
                          PTR_s__driver_jbd4010_jdb4010_status_i_00593988);
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1d < 0) goto LAB_00593720;
    }
    bVar2 = 1;
    goto LAB_0059372e;
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    param_3 = 0x332;
    FUN_0043d574(1,DAT_00593900,DAT_005938fc,PTR_s_am_devices_jbd4010_status_check__0059397c,0x332,
                 PTR_s_jdb4010_status_is_abnormal__reco_00593978);
  }
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1f < 0) {
LAB_005936de:
    compress_log_output(0x4000000,PTR_s__driver_jbd4010_jdb4010_status_i_00593980,
                        PTR_s__driver_jbd4010_jdb4010_status_i_00593980);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1d < 0) goto LAB_005936de;
  }
  jdb4010_status_recovery();
  bVar2 = 0;
LAB_0059372e:
  jbd4010_standby_mode();
  return CONCAT44(param_3,(uint)bVar2);
}

