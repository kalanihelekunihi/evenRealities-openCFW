
void smpScSendPubKey(int param_1,int param_2)

{
  int iVar1;
  
  DmConnSetIdle(*(undefined1 *)(param_1 + 0x3d),1,1);
  smpStartRspTimer(param_1);
  iVar1 = smpMsgAlloc(0x49);
  if (iVar1 == 0) {
    *(undefined1 *)(param_2 + 3) = 8;
    *(undefined1 *)(param_2 + 2) = 3;
    smpSmExecute(param_1,param_2);
  }
  else {
    *(undefined1 *)(iVar1 + 8) = 0xc;
    WStrReverseCpy(iVar1 + 9,*(undefined4 *)(*(int *)(param_1 + 0x48) + 0xc),0x20);
    WStrReverseCpy(iVar1 + 0x29,*(int *)(*(int *)(param_1 + 0x48) + 0xc) + 0x20,0x20);
    smpSendPkt(param_1,iVar1);
  }
  return;
}

