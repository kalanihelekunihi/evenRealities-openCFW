
void HciLeSetDataLen(undefined2 param_1,undefined2 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2022,6);
  if (iVar1 != 0) {
    *(char *)(iVar1 + 3) = (char)param_1;
    *(char *)(iVar1 + 4) = (char)((ushort)param_1 >> 8);
    *(char *)(iVar1 + 5) = (char)param_2;
    *(char *)(iVar1 + 6) = (char)((ushort)param_2 >> 8);
    *(char *)(iVar1 + 7) = (char)param_3;
    *(char *)(iVar1 + 8) = (char)((uint)param_3 >> 8);
    hciCmdSend(iVar1);
  }
  return;
}

