
undefined8
setting_respond_to_app_serialize
          (undefined4 param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint local_10;
  
  local_10 = param_4;
  iVar1 = FUN_0045a568();
  uVar2 = DAT_0049bffc;
  if (iVar1 == 1) {
    local_10 = 0x100;
    if (*DAT_0049bbf0 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x126;
        FUN_0043d574(1,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bfec,0x126,DAT_0049bff4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0049bff8);
      }
      uVar2 = 1;
    }
    else {
      FUN_0043c0e4(DAT_0049bffc,0x100,0);
      iVar1 = setting_respond_to_app(uVar2,&local_10);
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x12f;
          FUN_0043d574(1,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bfec,0x12f,DAT_0049c000);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0049c004,DAT_0049c004);
        }
        uVar2 = 0x2b;
      }
      else {
        iVar1 = FUN_0045a568();
        if (iVar1 == 1) {
          Thread_MsgPbTxByBle(1,9,uVar2,local_10 & 0xffff,param_2,param_3);
        }
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          param_2 = 0x136;
          FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bfec,0x136,DAT_0049c008);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10000000,PTR_s__pb_service_setting__Response_AP_0049c00c,
                              PTR_s__pb_service_setting__Response_AP_0049c00c);
        }
        uVar2 = 0;
      }
    }
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x11d;
      FUN_0043d574(4,DAT_0049bbc0,DAT_0049bbbc,DAT_0049bfec,0x11d,DAT_0049bfe8);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0049bff0,DAT_0049bff0);
    }
    uVar2 = 0;
  }
  return CONCAT44(param_2,uVar2);
}

