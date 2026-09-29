
void HciLeReadRemoteFeatCmd(undefined2 param_1)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2016,2);
  if (iVar1 != 0) {
    *(char *)(iVar1 + 3) = (char)param_1;
    *(char *)(iVar1 + 4) = (char)((ushort)param_1 >> 8);
    hciCmdSend(iVar1);
  }
  return;
}

