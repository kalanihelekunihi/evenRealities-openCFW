
void HciLeGenerateDHKey(undefined4 param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2026,0x40);
  if (iVar1 != 0) {
    FUN_00439be4(iVar1 + 3,param_1,0x20);
    FUN_00439be4(iVar1 + 0x23,param_2,0x20);
    hciCmdSend(iVar1);
  }
  return;
}

