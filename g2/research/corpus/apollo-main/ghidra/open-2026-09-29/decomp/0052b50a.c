
undefined4
HciLeSetScanParamCmd
          (undefined1 param_1,undefined2 param_2,undefined4 param_3,undefined4 param_4,
          undefined1 param_5)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x200b,7);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 3) = param_1;
    *(char *)(iVar1 + 4) = (char)param_2;
    *(char *)(iVar1 + 5) = (char)((ushort)param_2 >> 8);
    *(char *)(iVar1 + 6) = (char)param_3;
    *(char *)(iVar1 + 7) = (char)((uint)param_3 >> 8);
    *(char *)(iVar1 + 8) = (char)param_4;
    *(undefined1 *)(iVar1 + 9) = param_5;
    hciCmdSend(iVar1);
  }
  return param_4;
}

