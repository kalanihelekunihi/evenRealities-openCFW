
undefined4 DmPrivClearResList(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = WsfMsgAlloc(0x2c);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 2) = 0x33;
    WsfMsgSend(*(undefined1 *)(DAT_004d2924 + 0xc),iVar1);
  }
  return unaff_r7;
}

