
undefined8 AT_CoreInit(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  int iVar2;
  
  puVar1 = DAT_00541580;
  DAT_00541580[2] = DAT_00541584;
  puVar1[3] = (int)(DAT_00541588 - puVar1[2]) >> 4;
  FUN_0057ddfc();
  puVar1[1] = 0;
  *puVar1 = *puVar1 | 1;
  *puVar1 = *puVar1 | 2;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_1 = 0x5b;
    param_2 = DAT_0054158c;
    FUN_0043d574(4,DAT_00541598,DAT_00541594,DAT_00541590,0x5b,DAT_0054158c,puVar1[3],param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0054159c,DAT_0054159c,puVar1[3]);
  }
  return CONCAT44(param_2,param_1);
}

