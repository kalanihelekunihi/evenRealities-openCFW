
int FUN_004ecfc8(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar1 = FUN_004e9fd6();
  iVar3 = param_1 * 3;
  iVar4 = 0;
  for (iVar2 = iVar3; (iVar2 < iVar3 + 3 && (iVar2 < iVar1)); iVar2 = iVar2 + 1) {
    iVar4 = iVar4 + 1;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004ed6e4,DAT_004ed04c,DAT_004ed718,0x6fc,DAT_004ed714,param_1,iVar4,iVar1,
                 iVar3,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x11000000,DAT_004ed71c,DAT_004ed71c,param_1,iVar4,iVar1,iVar3);
  }
  return iVar4;
}

