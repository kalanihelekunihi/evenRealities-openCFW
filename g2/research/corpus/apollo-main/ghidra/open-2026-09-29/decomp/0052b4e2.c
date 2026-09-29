
undefined4
HciLeSetScanEnableCmd(undefined1 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x200c,2);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 3) = param_1;
    *(undefined1 *)(iVar1 + 4) = param_2;
    hciCmdSend(iVar1);
  }
  return param_4;
}

