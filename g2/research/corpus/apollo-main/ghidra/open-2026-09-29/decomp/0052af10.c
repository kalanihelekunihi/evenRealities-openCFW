
undefined4
HciDisconnectCmd(undefined2 param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = hciCmdAlloc(0x406,3);
  if (iVar1 != 0) {
    *(char *)(iVar1 + 3) = (char)param_1;
    *(char *)(iVar1 + 4) = (char)((ushort)param_1 >> 8);
    *(undefined1 *)(iVar1 + 5) = param_2;
    hciCmdSend(iVar1);
  }
  return param_4;
}

