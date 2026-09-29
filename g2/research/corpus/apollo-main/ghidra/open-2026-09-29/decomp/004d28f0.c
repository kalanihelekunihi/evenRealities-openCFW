
undefined4
DmPrivSetPrivacyMode(undefined1 param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = WsfMsgAlloc(0xc);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 2) = 0x35;
    *(undefined1 *)(iVar1 + 4) = param_1;
    FUN_004d293c(iVar1 + 5,param_2);
    *(undefined1 *)(iVar1 + 0xb) = param_3;
    WsfMsgSend(*(undefined1 *)(DAT_004d2924 + 0xc),iVar1);
  }
  return param_4;
}

