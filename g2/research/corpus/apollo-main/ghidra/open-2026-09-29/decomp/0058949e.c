
undefined4 FUN_0058949e(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = DAT_00589934;
  if (*(char *)(DAT_00589934 + 0xc4) != '\0') {
    *(char *)(DAT_00589934 + 0xc4) = *(char *)(DAT_00589934 + 0xc4) + -1;
  }
  if (*(char *)(iVar1 + 0xc4) == '\0') {
    *(undefined1 *)(iVar1 + 0xc3) = 0;
    *(undefined4 *)(iVar1 + 200) = 0;
    *(undefined4 *)(iVar1 + 0xcc) = 0;
    FUN_0058956e();
  }
  return unaff_r7;
}

