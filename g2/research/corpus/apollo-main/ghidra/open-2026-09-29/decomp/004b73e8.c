
void vendorCcbInitLike(void)

{
  int iVar1;
  byte bVar2;
  
  iVar1 = DAT_004b7430;
  for (bVar2 = 0; bVar2 < 3; bVar2 = bVar2 + 1) {
    FUN_0043c0e4(iVar1,0x30,0);
    *(undefined2 *)(iVar1 + 0xc) = 0xffff;
    *(undefined1 *)(iVar1 + 0x10) = 0;
    *(undefined1 *)(iVar1 + 0x11) = 0;
    *(undefined1 *)(iVar1 + 0x16) = 0;
    *(undefined1 *)(iVar1 + 0x2c) = 0;
    *(undefined1 *)(iVar1 + 0x19) = 0xff;
    iVar1 = iVar1 + 0x30;
  }
  return;
}

