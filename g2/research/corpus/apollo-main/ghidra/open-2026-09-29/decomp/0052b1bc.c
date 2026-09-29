
undefined4
HciLeWriteDefDataLen(undefined2 param_1,undefined2 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2024,4);
  if (iVar1 != 0) {
    *(char *)(iVar1 + 3) = (char)param_1;
    *(char *)(iVar1 + 4) = (char)((ushort)param_1 >> 8);
    *(char *)(iVar1 + 5) = (char)param_2;
    *(char *)(iVar1 + 6) = (char)((ushort)param_2 >> 8);
    hciCmdSend(iVar1);
  }
  return param_4;
}

