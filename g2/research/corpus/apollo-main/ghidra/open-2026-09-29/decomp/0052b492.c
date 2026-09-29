
void HciLeSetEventMaskCmd(undefined4 param_1)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2001,8);
  if (iVar1 != 0) {
    FUN_00439be4(iVar1 + 3,param_1,8);
    hciCmdSend(iVar1);
  }
  return;
}

