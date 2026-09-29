
undefined4
smprActSendSecurityReq(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  smpStartRspTimer(param_1);
  iVar1 = smpMsgAlloc(10);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 8) = 0xb;
    *(undefined1 *)(iVar1 + 9) = *(undefined1 *)(param_2 + 4);
    smpSendPkt(param_1);
  }
  return param_4;
}

