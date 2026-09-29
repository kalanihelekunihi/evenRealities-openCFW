
undefined4
RING_ConnectPolicyOnDominantHand(char param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  cVar1 = _GetState();
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f76c,0x70,DAT_0049f768,param_1,param_2,cVar1,
                 param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xcc00000,DAT_0049f770,DAT_0049f770,param_1,param_2,cVar1);
  }
  if (param_2 == param_1) {
    if (cVar1 == '\x01') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f76c,0x7a,DAT_0049f77c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0049f780,DAT_0049f780);
      }
    }
    else {
      _EnterState(2);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f76c,0x78,DAT_0049f774);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0049f778,DAT_0049f778);
      }
    }
    uVar3 = 1;
  }
  else if (cVar1 == '\x01') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0049f754,DAT_0049f750,DAT_0049f76c,0x82,DAT_0049f784,20000);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_0049f788,DAT_0049f788,20000);
    }
    uVar3 = 2;
  }
  else {
    _EnterState(1);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f76c,0x88,DAT_0049f78c,param_1,param_2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc800000,DAT_0049f790,DAT_0049f790,param_1,param_2);
    }
    uVar3 = 0;
  }
  return uVar3;
}

