
int DmAdvStart(byte param_1,int param_2,int param_3,int param_4)

{
  int iVar1;
  byte bVar2;
  
  iVar1 = WsfMsgAlloc(0xe);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 2) = 2;
    *(byte *)(iVar1 + 4) = param_1;
    bVar2 = 0;
    while( true ) {
      if (param_1 <= bVar2) break;
      *(undefined1 *)((uint)bVar2 + iVar1 + 5) = *(undefined1 *)(param_2 + (uint)bVar2);
      *(undefined2 *)(iVar1 + (uint)bVar2 * 2 + 8) = *(undefined2 *)(param_3 + (uint)bVar2 * 2);
      *(undefined1 *)((uint)bVar2 + iVar1 + 0xc) = *(undefined1 *)(param_4 + (uint)bVar2);
      bVar2 = bVar2 + 1;
    }
    WsfMsgSend(*(undefined1 *)(DAT_004b32d0 + 0xc),iVar1);
  }
  return param_4;
}

