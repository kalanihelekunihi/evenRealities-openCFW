
void FUN_0055bb3a(undefined1 param_1,undefined2 param_2,undefined2 param_3)

{
  int iVar1;
  uint uVar2;
  
  WsfTaskLock();
  uVar2 = DmScanPhyToIdx(param_1);
  iVar1 = DAT_0055bbbc;
  *(undefined2 *)(DAT_0055bbbc + (uVar2 & 0xff) * 2 + 0x10) = param_2;
  *(undefined2 *)(iVar1 + (uVar2 & 0xff) * 2 + 0x14) = param_3;
  WsfTaskUnlock();
  return;
}

