
undefined4 dmConnUpdActUpdateSlave(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if (((int)((uint)*(byte *)(param_1 + 0x28) << 0x1e) < 0) &&
     (iVar1 = HciGetLeSupFeat(), iVar1 << 0x1e < 0)) {
    HciLeConnUpdateCmd(*(undefined2 *)(param_1 + 0xc),param_2 + 4);
  }
  else if (*(char *)(param_1 + 0x11) == '\0') {
    *(undefined1 *)(param_1 + 0x11) = 1;
    L2cDmConnUpdateReq(*(undefined2 *)(param_1 + 0xc),param_2 + 4);
  }
  else {
    dmConnUpdateCback(param_1,0xc);
  }
  return param_4;
}

