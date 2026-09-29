
void smprActSendPairRandom(int param_1,int param_2)

{
  byte bVar1;
  int iVar2;
  
  if (*(byte *)(param_1 + 0x24) < *(byte *)(param_1 + 0x2b)) {
    bVar1 = *(byte *)(param_1 + 0x24);
  }
  else {
    bVar1 = *(byte *)(param_1 + 0x2b);
  }
  FUN_00439be4(*(int *)(param_1 + 0x30) + 0x20,*(undefined4 *)(param_2 + 4),bVar1);
  FUN_0043c0e4(*(int *)(param_1 + 0x30) + (uint)bVar1 + 0x20,0x10 - (uint)bVar1,0);
  *(undefined1 *)(param_1 + 0x44) = 1;
  smpStartRspTimer(param_1);
  iVar2 = smpMsgAlloc(0x19);
  if (iVar2 != 0) {
    *(undefined1 *)(iVar2 + 8) = 4;
    FUN_00439be4(iVar2 + 9,*(int *)(param_1 + 0x30) + 0x30,0x10);
    smpSendPkt(param_1,iVar2);
  }
  return;
}

