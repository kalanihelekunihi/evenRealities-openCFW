
void smpScActPkSendKeypress(int param_1,int param_2)

{
  int iVar1;
  
  if (*(char *)(*(int *)(param_1 + 0x48) + 2) != '\0') {
    smpStartRspTimer(param_1);
    iVar1 = smpMsgAlloc(10);
    if (iVar1 == 0) {
      *(undefined1 *)(param_2 + 3) = 8;
      *(undefined1 *)(param_2 + 2) = 3;
      smpSmExecute(param_1,param_2);
    }
    else {
      *(undefined1 *)(iVar1 + 8) = 0xe;
      *(undefined1 *)(iVar1 + 9) = *(undefined1 *)(param_2 + 4);
      smpSendPkt(param_1,iVar1);
    }
  }
  return;
}

