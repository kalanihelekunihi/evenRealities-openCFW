
undefined4 * semantic_get_orientation_vector(void)

{
  double dVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  float fVar5;
  float fVar6;
  
  iVar2 = DAT_004a60e4;
  if ((*(int *)(DAT_004a60e4 + 8) != 0) &&
     (uVar4 = (*(int *)(DAT_004a60e4 + 8) - 1U) % 0x14,
     (int)((uint)*(byte *)(uVar4 * 0x70 + DAT_004a60e4 + 0x10) << 0x1f) < 0)) {
    semantic_transform_vector(uVar4 * 0x70 + DAT_004a60e4 + 0x34,DAT_004a60d0);
    FUN_004397a8(*(float *)(uVar4 * 0x70 + iVar2 + 0x38) * *(float *)(uVar4 * 0x70 + iVar2 + 0x38) +
                 *(float *)(uVar4 * 0x70 + iVar2 + 0x3c) * *(float *)(uVar4 * 0x70 + iVar2 + 0x3c));
    fVar5 = (float)FUN_0050969c(*(float *)(uVar4 * 0x70 + iVar2 + 0x34) * -1.0);
    fVar6 = (float)FUN_0050969c(*(undefined4 *)(iVar2 + uVar4 * 0x70 + 0x38));
    puVar3 = DAT_004a6580;
    *DAT_004a6580 = 0;
    dVar1 = DAT_004a5ee4;
    puVar3[1] = (float)((double)fVar5 * DAT_004a5ee4);
    puVar3[2] = (float)((double)fVar6 * dVar1);
  }
  return DAT_004a6580;
}

