
undefined8 _GetState(undefined4 param_1,undefined4 param_2)

{
  byte bVar1;
  byte *pbVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  
  pbVar2 = DAT_0049f744;
  if (*DAT_0049f744 == 0) {
    bVar1 = *DAT_0049f744;
  }
  else {
    uVar3 = _ring_policy_timeout_for_mode(*DAT_0049f744);
    if ((uVar3 != 0) &&
       (uVar4 = _ring_policy_elapsed_ticks(*(undefined4 *)(pbVar2 + 4)), uVar3 <= uVar4)) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        param_2 = 0x56;
        FUN_0043d574(4,DAT_0049f754,DAT_0049f750,DAT_0049f74c,0x56,DAT_0049f748,*pbVar2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x10400000,DAT_0049f758,DAT_0049f758,*pbVar2);
      }
      *pbVar2 = 0;
      pbVar2[4] = 0;
      pbVar2[5] = 0;
      pbVar2[6] = 0;
      pbVar2[7] = 0;
      pbVar2[8] = 0;
    }
    bVar1 = *pbVar2;
  }
  return CONCAT44(param_2,(uint)bVar1);
}

