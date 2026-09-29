
void dmConnSetScanInterval(undefined1 param_1,undefined2 param_2,undefined2 param_3)

{
  int iVar1;
  uint uVar2;
  
  WsfTaskLock();
  uVar2 = DmInitPhyToIdx(param_1);
  iVar1 = DAT_004b7430;
  *(undefined2 *)(DAT_004b7430 + (uVar2 & 0xff) * 2 + 0xbc) = param_2;
  *(undefined2 *)(iVar1 + (uVar2 & 0xff) * 2 + 0xc0) = param_3;
  WsfTaskUnlock();
  return;
}

