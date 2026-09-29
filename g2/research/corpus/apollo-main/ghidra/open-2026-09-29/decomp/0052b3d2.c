
void HciLeSetAdvDataCmd(byte param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2008,0x20);
  if (iVar1 != 0) {
    *(byte *)(iVar1 + 3) = param_1;
    FUN_00439be4(iVar1 + 4,param_2,param_1);
    FUN_0043c0e4(iVar1 + 4 + (uint)param_1,0x1f - (uint)param_1,0);
    hciCmdSend(iVar1);
  }
  return;
}

