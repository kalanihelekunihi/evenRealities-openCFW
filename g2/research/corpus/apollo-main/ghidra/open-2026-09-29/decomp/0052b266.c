
void HciLeEncryptCmd(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2017,0x20);
  if (iVar1 != 0) {
    FUN_00439be4(iVar1 + 3,param_1,0x10);
    FUN_00439be4(iVar1 + 0x13,param_2,0x10);
    hciCmdSend(iVar1);
  }
  return;
}

