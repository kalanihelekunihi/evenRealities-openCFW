
undefined4
uled_rw_param_validate(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if (param_1 == 0) {
    uVar2 = param_2;
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x98;
      uVar2 = DAT_0059d1ac;
      param_3 = param_2;
      FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d1b0,0x98,DAT_0059d1ac,param_2,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0059d1b4,DAT_0059d1b4,param_2,param_1,uVar2,param_3);
    }
    uVar2 = 0xffffffff;
  }
  else if (*(int *)(param_1 + 0x18) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d1b0,0x9d,DAT_0059d1b8,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0059d1bc,DAT_0059d1bc,param_2);
    }
    uVar2 = 0xffffffff;
  }
  else if (*(int *)(param_1 + 0x14) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0059d174,DAT_0059d170,DAT_0059d1b0,0xa2,DAT_0059d1c0,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0059d1c4,DAT_0059d1c4,param_2);
    }
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

