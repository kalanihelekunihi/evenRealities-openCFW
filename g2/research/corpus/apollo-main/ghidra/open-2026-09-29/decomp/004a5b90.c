
undefined8 semantic_get_latest_complete_sample(void)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int local_1c [3];
  
  iVar4 = 0;
  for (uVar5 = 0; uVar6 = 0, uVar5 < 0x14; uVar5 = uVar5 + 1) {
    uVar6 = (((*(int *)(DAT_004a60e4 + 8) + 0x13U) % 0x14 + 0x14) - uVar5) % 0x14;
    iVar7 = uVar6 * 0x70 + DAT_004a60e4;
    iVar9 = uVar6 * 0x70 + DAT_004a60e4;
    iVar8 = uVar6 * 0x70 + DAT_004a60e4;
    if (((*(float *)(iVar7 + 0x40) == 0.0) && (*(float *)(iVar7 + 0x44) == 0.0)) &&
       (*(float *)(iVar7 + 0x48) == 0.0)) {
      bVar1 = false;
    }
    else {
      bVar1 = true;
    }
    if (((*(float *)(iVar9 + 0x34) == 0.0) && (*(float *)(iVar9 + 0x38) == 0.0)) &&
       (*(float *)(iVar9 + 0x3c) == 0.0)) {
      bVar2 = false;
    }
    else {
      bVar2 = true;
    }
    if (((*(float *)(iVar8 + 0x4c) == 0.0) && (*(float *)(iVar8 + 0x50) == 0.0)) &&
       (*(float *)(iVar8 + 0x54) == 0.0)) {
      bVar3 = false;
    }
    else {
      bVar3 = true;
    }
    if (((bVar1) && (bVar2)) && (bVar3)) break;
  }
  local_1c[0] = uVar6 * 0x70 + DAT_004a60e4 + 0x40;
  local_1c[1] = uVar6 * 0x70 + DAT_004a60e4 + 0x34;
  local_1c[2] = uVar6 * 0x70 + DAT_004a60e4 + 0x4c;
  for (iVar7 = 0; iVar7 < 3; iVar7 = iVar7 + 1) {
    for (iVar8 = 0; iVar8 < 3; iVar8 = iVar8 + 1) {
      iVar9 = local_1c[iVar7];
      for (uVar5 = 0; uVar5 < 4; uVar5 = uVar5 + 1) {
        *(undefined1 *)(DAT_004a6574 + iVar4) = *(undefined1 *)(iVar9 + iVar8 * 4 + uVar5);
        iVar4 = iVar4 + 1;
      }
    }
  }
  return CONCAT44(local_1c[0],DAT_004a6574);
}

