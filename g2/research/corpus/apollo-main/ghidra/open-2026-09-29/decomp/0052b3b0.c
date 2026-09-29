
void HciLeSetAdvEnableCmd(undefined1 param_1)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x200a,1);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 3) = param_1;
    hciCmdSend(iVar1);
  }
  return;
}

