
undefined4 DmAdvStop(byte param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  byte bVar2;
  
  iVar1 = WsfMsgAlloc(8);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 2) = 3;
    *(byte *)(iVar1 + 4) = param_1;
    bVar2 = 0;
    while( true ) {
      if (param_1 <= bVar2) break;
      *(undefined1 *)((uint)bVar2 + iVar1 + 5) = *(undefined1 *)(param_2 + (uint)bVar2);
      bVar2 = bVar2 + 1;
    }
    WsfMsgSend(*(undefined1 *)(DAT_004b32d0 + 0xc),iVar1);
  }
  return param_4;
}

