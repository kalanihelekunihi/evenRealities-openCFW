
undefined4
smpSendPairingFailed(undefined4 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = smpMsgAlloc(10);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 8) = 5;
    *(undefined1 *)(iVar1 + 9) = param_2;
    smpSendPkt(param_1,iVar1);
  }
  return param_4;
}

