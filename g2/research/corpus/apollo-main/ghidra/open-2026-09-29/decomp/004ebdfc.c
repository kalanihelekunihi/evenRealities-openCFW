
undefined8 FUN_004ebdfc(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  
  piVar1 = DAT_004ec298;
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x4c3;
      FUN_0043d574(1,DAT_004ebf1c,DAT_004ec294,DAT_004ec290,0x4c3,DAT_004ec21c,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ec224,DAT_004ec224);
    }
    uVar3 = 0xffffffff;
  }
  else {
    if (*DAT_004ec298 != 0) {
      ui_common_api_fn_00509c96(*DAT_004ec298);
      *piVar1 = 0;
    }
    iVar2 = ui_common_api_fn_00509c1c();
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x4cf;
        FUN_0043d574(1,DAT_004ebf1c,DAT_004ec294,DAT_004ec290,0x4cf,DAT_004ec29c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004ec2a0);
      }
      uVar3 = 0xffffffff;
    }
    else {
      *DAT_004ec2a4 = 1;
      *(undefined1 *)(DAT_004ec248 + 0x124) = 0;
      FUN_004eb7b8(param_1);
      iVar2 = FUN_004ebf20();
      FUN_0050012e(iVar2 + 1);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        param_2 = 0x4d9;
        FUN_0043d574(3,DAT_004ebf1c,DAT_004ec294,DAT_004ec290,0x4d9,DAT_004ec2a8);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004ec2ac,DAT_004ec2ac);
      }
      uVar3 = 0;
    }
  }
  return CONCAT44(param_2,uVar3);
}

