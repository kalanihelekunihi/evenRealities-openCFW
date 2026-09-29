
undefined4
HciLeSetPhyCmd(undefined2 param_1,undefined1 param_2,undefined1 param_3,undefined4 param_4,
              undefined4 param_5)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x2032,7);
  if (iVar1 != 0) {
    *(char *)(iVar1 + 3) = (char)param_1;
    *(char *)(iVar1 + 4) = (char)((ushort)param_1 >> 8);
    *(undefined1 *)(iVar1 + 5) = param_2;
    *(undefined1 *)(iVar1 + 6) = param_3;
    *(char *)(iVar1 + 7) = (char)param_4;
    *(char *)(iVar1 + 8) = (char)param_5;
    *(char *)(iVar1 + 9) = (char)((uint)param_5 >> 8);
    hciCmdSend(iVar1);
  }
  return param_4;
}

