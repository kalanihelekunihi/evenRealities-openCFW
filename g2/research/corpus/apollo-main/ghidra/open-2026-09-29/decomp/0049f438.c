
undefined8
RING_ConnectPolicyMarkRingConnectInfoProcessed
          (uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_0049f7a8;
  if ((param_1 & 0xff) != 0) {
    iVar2 = _ring_policy_tick_now();
    *piVar1 = iVar2;
    if (*piVar1 == 0) {
      *piVar1 = 1;
    }
    iVar2 = _GetState();
    if (iVar2 == 1) {
      *(undefined1 *)(DAT_0049f744 + 8) = 1;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_1 = 0xb3;
      param_2 = DAT_0049f7b4;
      FUN_0043d574(3,DAT_0049f754,DAT_0049f750,DAT_0049f7b8,0xb3,DAT_0049f7b4,*piVar1,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0049f7bc,DAT_0049f7bc,*piVar1);
    }
  }
  return CONCAT44(param_2,param_1);
}

