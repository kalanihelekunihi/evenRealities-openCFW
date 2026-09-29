
undefined4
RING_ConnectPolicyShouldBlockRingConnectInfo
          (char param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  
  if (param_1 == '\0') {
    uVar1 = 0;
  }
  else {
    iVar2 = _GetState();
    if (iVar2 == 1) {
      if (*(char *)(DAT_0049f744 + 8) == '\0') {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f798,0x95,DAT_0049f794,param_3,param_4);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_0049f79c,DAT_0049f79c);
        }
        uVar1 = 0;
      }
      else {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(2,DAT_0049f754,DAT_0049f750,DAT_0049f798,0x98,DAT_0049f7a0,param_3,param_4);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x8000000,DAT_0049f7a4);
        }
        uVar1 = 1;
      }
    }
    else if ((*DAT_0049f7a8 == 0) ||
            (uVar3 = _ring_policy_elapsed_ticks(*DAT_0049f7a8), 19999 < uVar3)) {
      uVar1 = 0;
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(2,DAT_0049f754,DAT_0049f750,DAT_0049f798,0xa0,DAT_0049f7ac,20000,param_4);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0049f7b0,DAT_0049f7b0,20000);
      }
      uVar1 = 1;
    }
  }
  return uVar1;
}

