
void HciLeLtkReqReplCmd(undefined2 param_1,undefined4 param_2)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x201a,0x12);
  if (iVar1 != 0) {
    *(char *)(iVar1 + 3) = (char)param_1;
    *(char *)(iVar1 + 4) = (char)((ushort)param_1 >> 8);
    FUN_00439be4(iVar1 + 5,param_2,0x10);
    hciCmdSend(iVar1);
  }
  return;
}

