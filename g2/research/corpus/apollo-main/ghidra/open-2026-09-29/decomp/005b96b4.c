
void FUN_005b96b4(void)

{
  int iVar1;
  int iVar2;
  
  *DAT_005b9b00 = 0;
  *DAT_005b9c88 = 0;
  *DAT_005b9c98 = 0;
  *DAT_005b9cb0 = 0;
  *DAT_005b9cb4 = 0;
  *DAT_005b9cc0 = 0;
  *DAT_005b9cc8 = 0;
  for (iVar2 = 0; iVar2 < 3; iVar2 = iVar2 + 1) {
    *(undefined4 *)(DAT_005b9c44 + iVar2 * 4) = 0;
    iVar1 = DAT_005b9a64;
    *(undefined4 *)(DAT_005b9a64 + iVar2 * 0xc) = 0;
    *(undefined4 *)(iVar2 * 0xc + iVar1 + 4) = 0;
    *(undefined1 *)(iVar2 * 0xc + iVar1 + 8) = 0;
  }
  *DAT_005b9c78 = 0;
  *DAT_005b9c7c = 0;
  *DAT_005b9afc = 0;
  *DAT_005b9c60 = 0;
  return;
}

