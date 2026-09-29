
void FUN_005a3e24(void)

{
  int iVar1;
  uint *puVar2;
  int *piVar3;
  
  piVar3 = DAT_005a48e8;
  puVar2 = DAT_005a45c8;
  iVar1 = DAT_005a4104;
  *DAT_005a45c8 =
       *DAT_005a45c8 & 0xffffc3ff |
       (*(uint *)(DAT_005a4104 + *DAT_005a48e8 * 4 + 4) >> 0x11 & 0xf) << 10;
  *puVar2 = *puVar2 & 0xfffffc00 | *(uint *)(iVar1 + *piVar3 * 4 + 4) >> 7 & 0x3ff;
  *DAT_005a48ec = *DAT_005a48ec & 0xffffff80 | *(uint *)(iVar1 + *piVar3 * 4 + 4) >> 0x15 & 0x7f;
  *DAT_005a45cc = 0;
  return;
}

