
undefined4 anccActionListPop(void)

{
  int iVar1;
  ushort uVar2;
  
  iVar1 = DAT_004bf6c0;
  uVar2 = 0;
  while( true ) {
    if (0x3f < uVar2) {
      return 0;
    }
    if (*(char *)((uint)uVar2 * -0xc + DAT_004bf6c0 + 0x318) == '\x01') break;
    uVar2 = uVar2 + 1;
  }
  *(undefined1 *)((uint)uVar2 * -0xc + DAT_004bf6c0 + 0x318) = 0;
  *(ushort *)(iVar1 + 8) = 0x3f - uVar2;
  return 1;
}

