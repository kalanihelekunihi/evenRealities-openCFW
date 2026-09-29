
undefined4 setting_notify_device_status_to_app(void)

{
  int iVar1;
  undefined4 uVar2;
  undefined1 auStack_70 [104];
  
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    FUN_0048949c(auStack_70,0x68);
    iVar1 = setting_build_full_status_package(auStack_70);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0049c02c,DAT_0049c028,PTR_s_setting_notify_device_status_to__0049c054,
                     0x197,DAT_0049bfd4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0049bfdc,DAT_0049bfdc);
      }
      uVar2 = 0x2b;
    }
    else {
      uVar2 = setting_notify_common(auStack_70);
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0049c02c,DAT_0049c028,PTR_s_setting_notify_device_status_to__0049c054,400,
                   DAT_0049bfe8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0049bff0,DAT_0049bff0);
    }
    uVar2 = 0;
  }
  return uVar2;
}

