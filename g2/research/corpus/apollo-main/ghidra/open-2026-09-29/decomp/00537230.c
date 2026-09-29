
void L2cDmConnUpdateRsp(undefined1 param_1,undefined2 param_2,undefined4 param_3)

{
  int iVar1;
  
  iVar1 = l2cMsgAlloc(0xe);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 8) = 0x13;
    *(undefined1 *)(iVar1 + 9) = param_1;
    *(undefined1 *)(iVar1 + 10) = 2;
    *(undefined1 *)(iVar1 + 0xb) = 0;
    *(char *)(iVar1 + 0xc) = (char)param_3;
    *(char *)(iVar1 + 0xd) = (char)((uint)param_3 >> 8);
    L2cDataReq(5,param_2,6);
  }
  return;
}

