
undefined4 smpScSendPairCnf(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  DmConnSetIdle(*(undefined1 *)(param_1 + 0x3d),1,1);
  smpStartRspTimer(param_1);
  iVar1 = smpMsgAlloc(0x19);
  if (iVar1 == 0) {
    *(undefined1 *)(param_2 + 3) = 8;
    *(undefined1 *)(param_2 + 2) = 3;
    smpSmExecute(param_1,param_2);
  }
  else {
    *(undefined1 *)(iVar1 + 8) = 3;
    WStrReverseCpy(iVar1 + 9,param_3,0x10);
    smpSendPkt(param_1,iVar1);
  }
  return param_4;
}

