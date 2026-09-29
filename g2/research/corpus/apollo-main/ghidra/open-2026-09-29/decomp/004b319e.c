
void DmAdvSetData(undefined1 param_1,undefined1 param_2,undefined1 param_3,byte param_4,
                 undefined4 param_5)

{
  int iVar1;
  
  iVar1 = WsfMsgAlloc(param_4 + 8);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 2) = 1;
    *(undefined1 *)(iVar1 + 4) = param_1;
    *(undefined1 *)(iVar1 + 5) = param_2;
    *(undefined1 *)(iVar1 + 6) = param_3;
    *(byte *)(iVar1 + 7) = param_4;
    FUN_00439be4(iVar1 + 8,param_5,param_4);
    WsfMsgSend(*(undefined1 *)(DAT_004b32d0 + 0xc),iVar1);
  }
  return;
}

