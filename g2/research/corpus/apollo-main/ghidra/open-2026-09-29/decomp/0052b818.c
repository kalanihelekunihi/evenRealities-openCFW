
undefined4
HciLeSetPrivacyModeCmd(undefined1 param_1,undefined4 param_2,undefined1 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x204e,8);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 3) = param_1;
    FUN_004d293c(iVar1 + 4,param_2);
    *(undefined1 *)(iVar1 + 10) = param_3;
    hciCmdSend(iVar1);
  }
  return param_4;
}

