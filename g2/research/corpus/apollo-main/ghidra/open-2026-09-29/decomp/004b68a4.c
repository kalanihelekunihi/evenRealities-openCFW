
undefined4
dmConnHciHandler(ushort *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (((char)param_1[1] == '\x01') || ((char)param_1[1] == '\x02')) {
    iVar1 = dmConnCcbByBdAddr(param_1 + 5);
    if ((((iVar1 == 0) && (iVar1 = dmConnCmplStates(), iVar1 == 0)) &&
        (*(char *)((int)param_1 + 3) == '\0')) && ((char)param_1[4] == '\x01')) {
      iVar1 = dmConnCcbAlloc(param_1 + 5);
    }
    if (*(char *)((int)param_1 + 3) == '\0') {
      *(undefined1 *)(param_1 + 1) = 0x1c;
    }
    else {
      *(undefined1 *)(param_1 + 1) = 0x1b;
    }
  }
  else {
    iVar1 = dmConnCcbByHandle(*param_1);
    *(char *)(param_1 + 1) = (char)param_1[1] + '\x1a';
  }
  if (iVar1 != 0) {
    *param_1 = (ushort)*(byte *)(iVar1 + 0x10);
    dmConnSmExecute(iVar1,param_1);
  }
  return param_4;
}

