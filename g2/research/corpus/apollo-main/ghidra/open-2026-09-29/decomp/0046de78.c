
undefined8 appSlaveConnOpen(ushort *param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_0046eb18;
  *DAT_0046eb18 = DAT_0046e064 + (uint)*param_1 * 0x30 + -0x30;
  *(char *)(*DAT_0046eb8c + 0x54) = (char)*param_1;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_3 = *piVar1;
    param_1 = (ushort *)0x129;
    param_2 = DAT_0046e068;
    FUN_0043d574(4,DAT_0046dff8,DAT_0046dff4,DAT_0046e06c,0x129,DAT_0046e068,param_3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_0046e070,DAT_0046e070,*piVar1,param_1,param_2,param_3);
  }
  return CONCAT44(param_2,param_1);
}

