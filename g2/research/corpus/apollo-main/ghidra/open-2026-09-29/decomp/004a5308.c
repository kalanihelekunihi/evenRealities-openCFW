
void semantic_forward_periodic_sample(void)

{
  uint *puVar1;
  int iVar2;
  
  puVar1 = DAT_004a5edc;
  if ((uint)((ulonglong)*DAT_004a5ecc /
            ((ulonglong)
             (uint)(*(int *)((uint)*DAT_004a5ee0 * 0x10 + DAT_004a5ed8 + 4) *
                   *(int *)((uint)*DAT_004a5ee0 * 0x10 + DAT_004a5ed8 + 0xc)) / 1000)) <=
      *DAT_004a5edc) {
    *DAT_004a5edc = 0;
    iVar2 = *(int *)(DAT_004a5698 + 8) + -1;
    FUN_004da6d4(*(undefined4 *)(iVar2 * 0x70 + DAT_004a5698 + 0x34),
                 *(undefined4 *)(iVar2 * 0x70 + DAT_004a5698 + 0x38),
                 *(undefined4 *)(iVar2 * 0x70 + DAT_004a5698 + 0x3c));
  }
  *puVar1 = *puVar1 + 1;
  return;
}

