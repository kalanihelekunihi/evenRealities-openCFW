
undefined4 pt_cmd_38_handler(int param_1,byte param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_005735f4,DAT_005735f0,DAT_00573c34,0x8ef,DAT_00573c28);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0057335c;
  }
  compress_log_output(0xc000000,DAT_00573c2c,DAT_00573c2c);
LAB_0057335c:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     (param_2 < 5)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005735f4,DAT_005735f0,DAT_00573c34,0x8f2,DAT_00573c20,DAT_00573c34);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00573c30,DAT_00573c30,DAT_00573c34);
    }
    uVar2 = 0xffffffff;
  }
  else {
    param_1 = param_1 + 4;
    *param_3 = 0x1c;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    iVar1 = productModeGet();
    if (iVar1 == 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(3,DAT_005735f4,DAT_005735f0,DAT_00573c34,0x902,DAT_00573c38,param_1,0xe);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc800000,DAT_00573f64,DAT_00573f64,param_1,0xe);
      }
      SVC_WritePSNToOTP(param_1);
      SVC_NvdbWriteSysData(0,param_1);
      uVar2 = SVC_NvdbReadSysData(0);
      iVar1 = FUN_004751c8(param_1,uVar2,0xe);
      if (iVar1 == 0) {
        param_3[4] = 0;
      }
      else {
        param_3[4] = 1;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005735f4,DAT_005735f0,DAT_00573c34,0x914,DAT_00573f68);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_005741cc,DAT_005741cc);
      }
      param_3[4] = 5;
    }
    *param_4 = 5;
    uVar2 = 0;
  }
  return uVar2;
}

