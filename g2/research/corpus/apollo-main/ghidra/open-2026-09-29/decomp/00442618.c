
undefined1 FUN_00442618(int param_1)

{
  int iVar1;
  
  iVar1 = 0;
  while( true ) {
    if (*DAT_00442cd4 <= iVar1) {
      return 2;
    }
    if ((*(int *)(DAT_00442cd8 + iVar1 * 0x10) == param_1) &&
       (*(int *)(iVar1 * 0x10 + DAT_00442cd8 + 8) != 0)) break;
    iVar1 = iVar1 + 1;
  }
  return *(undefined1 *)(*(int *)(DAT_00442cd8 + iVar1 * 0x10 + 0xc) + 0xb);
}

