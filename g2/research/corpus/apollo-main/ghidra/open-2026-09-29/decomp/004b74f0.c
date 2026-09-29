
void bleAttCback(int param_1)

{
  int iVar1;
  
  iVar1 = WsfMsgAlloc(*(short *)(param_1 + 8) + 0x10);
  if (iVar1 != 0) {
    FUN_00439be4(iVar1,param_1,0x10);
    *(int *)(iVar1 + 4) = iVar1 + 0x10;
    FUN_00439be4(*(undefined4 *)(iVar1 + 4),*(undefined4 *)(param_1 + 4),
                 *(undefined2 *)(param_1 + 8));
    WsfMsgSend(*(undefined1 *)(DAT_004b81fc + 0x56),iVar1);
  }
  return;
}

