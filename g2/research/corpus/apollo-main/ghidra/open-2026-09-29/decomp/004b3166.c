
void DmAdvConfig(undefined1 param_1,undefined1 param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = WsfMsgAlloc(0xe);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 2) = 0;
    *(undefined1 *)(iVar1 + 5) = param_2;
    *(undefined1 *)(iVar1 + 4) = param_1;
    *(undefined1 *)(iVar1 + 6) = param_3;
    FUN_004d293c(iVar1 + 7,param_4);
    WsfMsgSend(*(undefined1 *)(DAT_004b32d0 + 0xc),iVar1);
  }
  return;
}

