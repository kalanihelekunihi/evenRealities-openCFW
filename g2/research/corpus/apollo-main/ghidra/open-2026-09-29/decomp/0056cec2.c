
undefined8
SmpScCmac(undefined4 param_1,undefined4 param_2,undefined1 param_3,int param_4,int param_5)

{
  byte bVar1;
  int iVar2;
  
  bVar1 = *(byte *)(param_4 + 0x3d);
  iVar2 = FUN_0053665c(param_1,param_2,param_3,*(undefined1 *)(DAT_0056d81c + 0xec));
  if (iVar2 == 0) {
    WsfBufFree(param_2);
    *(undefined1 *)(param_5 + 3) = 8;
    *(undefined1 *)(param_5 + 2) = 3;
    smpSmExecute(param_4,param_5);
  }
  return CONCAT44(0x1c,(uint)bVar1);
}

