
undefined4 FUN_0055bb1e(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = WsfMsgAlloc(4);
  if (iVar1 != 0) {
    *(undefined1 *)(iVar1 + 2) = 0x11;
    WsfMsgSend(*(undefined1 *)(DAT_0055bbc0 + 0xc),iVar1);
  }
  return unaff_r7;
}

