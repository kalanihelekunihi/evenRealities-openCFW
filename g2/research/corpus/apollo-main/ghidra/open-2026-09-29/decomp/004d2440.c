
undefined4
dmSecMsgHandler(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = dmConnCcbById((char)*param_1);
  if (iVar1 != 0) {
    if (*(char *)(param_1 + 1) == '(') {
      DmConnSetIdle(*(undefined1 *)(iVar1 + 0x10),2,1);
      *(undefined1 *)(iVar1 + 0x18) = *(undefined1 *)(param_1 + 0xf);
      *(undefined1 *)(iVar1 + 0x12) = 1;
      HciLeStartEncryptionCmd(*(undefined2 *)(iVar1 + 0xc),param_1 + 10,param_1[0xe],param_1 + 2);
    }
    else if (*(char *)(param_1 + 1) == ')') {
      if (*(char *)(param_1 + 10) == '\0') {
        DmConnSetIdle(*(undefined1 *)(iVar1 + 0x10),2,0);
        HciLeLtkReqNegReplCmd(*(undefined2 *)(iVar1 + 0xc));
      }
      else {
        *(undefined1 *)(iVar1 + 0x18) = *(undefined1 *)((int)param_1 + 0x15);
        HciLeLtkReqReplCmd(*(undefined2 *)(iVar1 + 0xc),param_1 + 2);
      }
    }
  }
  return param_4;
}

