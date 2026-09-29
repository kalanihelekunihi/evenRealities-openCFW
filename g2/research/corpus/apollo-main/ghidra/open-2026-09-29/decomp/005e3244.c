
void smpiActProcPairCnf(int param_1,int param_2)

{
  int iVar1;
  
  FUN_00439be4(*(int *)(param_1 + 0x30) + 0x20,*(int *)(param_2 + 4) + 9,0x10);
  *(undefined1 *)(param_1 + 0x3f) = 4;
  smpStartRspTimer(param_1);
  iVar1 = smpMsgAlloc(0x19);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 8) = 4;
    FUN_00439be4(iVar1 + 9,*(int *)(param_1 + 0x30) + 0x30,0x10);
    smpSendPkt(param_1,iVar1);
  }
  return;
}

