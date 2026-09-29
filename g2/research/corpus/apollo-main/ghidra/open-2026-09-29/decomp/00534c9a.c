
undefined4
attsErrRsp(undefined4 param_1,undefined1 param_2,undefined1 param_3,undefined4 param_4,
          undefined1 param_5)

{
  int iVar1;
  
  iVar1 = attMsgAlloc(0xd);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 8) = 1;
    *(undefined1 *)(iVar1 + 9) = param_3;
    *(char *)(iVar1 + 10) = (char)param_4;
    *(char *)(iVar1 + 0xb) = (char)((uint)param_4 >> 8);
    *(undefined1 *)(iVar1 + 0xc) = param_5;
    attL2cDataReq(param_1,param_2,5,iVar1);
  }
  return param_4;
}

