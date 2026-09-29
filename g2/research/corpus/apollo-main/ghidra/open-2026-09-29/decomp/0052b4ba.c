
void HciLeSetRandAddrCmd(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2005,6);
  if (iVar1 != 0) {
    FUN_004d293c(iVar1 + 3,param_1);
    hciCmdSend(iVar1);
  }
  return;
}

