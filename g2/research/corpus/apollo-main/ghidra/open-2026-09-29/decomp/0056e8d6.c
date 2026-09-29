
undefined4 smpActSendPairCnf(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  int iVar2;
  
  if (*(char *)(param_1 + 0x3a) == '\0') {
    uVar1 = 4;
  }
  else {
    uVar1 = 3;
  }
  *(undefined1 *)(param_1 + 0x3f) = uVar1;
  smpStartRspTimer(param_1);
  iVar2 = smpMsgAlloc(0x19);
  if (iVar2 != 0) {
    *(undefined1 *)(iVar2 + 8) = 3;
    FUN_00439be4(iVar2 + 9,*(undefined4 *)(param_2 + 4),0x10);
    smpSendPkt(param_1,iVar2);
  }
  return param_4;
}

