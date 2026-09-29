
void bleDmCback(int param_1)

{
  ushort uVar1;
  int iVar2;
  ushort uVar3;
  
  uVar1 = DmSizeOfEvt(param_1);
  if (*(char *)(param_1 + 2) == '&') {
    uVar3 = (ushort)*(byte *)(param_1 + 8);
  }
  else {
    uVar3 = 0;
  }
  iVar2 = WsfMsgAlloc(uVar3 + uVar1);
  if (iVar2 != 0) {
    FUN_00439be4(iVar2,param_1,uVar1);
    if (*(char *)(param_1 + 2) == '&') {
      *(uint *)(iVar2 + 4) = iVar2 + (uint)uVar1;
      FUN_00439be4(*(undefined4 *)(iVar2 + 4),*(undefined4 *)(param_1 + 4),uVar3);
    }
    WsfMsgSend(*(undefined1 *)(DAT_004b81fc + 0x56),iVar2);
  }
  return;
}

