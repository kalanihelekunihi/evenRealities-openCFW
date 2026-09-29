
int FUN_100041b8(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = FUN_10003110();
  if ((*(uint *)(DAT_10004208 + 4) != 0) &&
     ((iVar2 = 0, *(char *)(DAT_10004208 + 0x370) == '\0' ||
      ((iVar2 = 1, 1 < *(uint *)(DAT_10004208 + 4) && (*(char *)(DAT_10004208 + 0x371) == '\0'))))))
  {
    *(undefined1 *)(DAT_10004208 + iVar2 + 0x370) = 1;
    FUN_10004a48(0x19,1);
    FUN_1000311c(uVar1);
    return iVar2;
  }
  FUN_1000311c(uVar1);
  return -1;
}

