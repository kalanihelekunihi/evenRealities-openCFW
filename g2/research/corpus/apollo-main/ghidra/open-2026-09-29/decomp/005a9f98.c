
void af_latin_hints_link_segments(int param_1,int param_2,int param_3,byte param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  
  iVar1 = param_1 + (uint)param_4 * 0x544;
  uVar5 = *(uint *)(iVar1 + 0x34);
  uVar7 = *(int *)(iVar1 + 0x2c) * 0x2c + uVar5;
  if (param_2 == 0) {
    iVar2 = 0;
  }
  else {
    iVar2 = *(int *)(param_3 + param_2 * 0xc + -0xc);
  }
  iVar4 = (*(int *)(*(int *)(param_1 + 0xabc) + 0x28) << 3) / 0x800;
  if (iVar4 == 0) {
    iVar4 = 1;
  }
  iVar6 = *(int *)(*(int *)(param_1 + 0xabc) + 0x28);
  for (uVar10 = uVar5; uVar10 < uVar7; uVar10 = uVar10 + 0x2c) {
    uVar11 = uVar5;
    if (*(char *)(uVar10 + 1) == *(char *)(iVar1 + 0x44)) {
      for (; uVar11 < uVar7; uVar11 = uVar11 + 0x2c) {
        if (((int)*(char *)(uVar11 + 1) + (int)*(char *)(uVar10 + 1) == 0) &&
           ((int)*(short *)(uVar10 + 2) < (int)*(short *)(uVar11 + 2))) {
          iVar9 = (int)*(short *)(uVar10 + 6);
          iVar3 = (int)*(short *)(uVar10 + 8);
          if (iVar9 < *(short *)(uVar11 + 6)) {
            iVar9 = (int)*(short *)(uVar11 + 6);
          }
          if (*(short *)(uVar11 + 8) < iVar3) {
            iVar3 = (int)*(short *)(uVar11 + 8);
          }
          if (iVar4 <= iVar3 - iVar9) {
            iVar8 = (int)*(short *)(uVar11 + 2) - (int)*(short *)(uVar10 + 2);
            if (iVar2 != 0) {
              iVar8 = (iVar8 * 0x400) / iVar2 + -0x400;
              if (iVar8 < 0x2711) {
                if (iVar8 < 1) {
                  iVar8 = 0;
                }
                else {
                  iVar8 = (iVar8 * iVar8) / 3000;
                }
              }
              else {
                iVar8 = 32000;
              }
            }
            iVar8 = ((iVar6 * 6000) / 0x800) / (iVar3 - iVar9) + iVar8;
            if (iVar8 < *(int *)(uVar10 + 0x1c)) {
              *(int *)(uVar10 + 0x1c) = iVar8;
              *(uint *)(uVar10 + 0x14) = uVar11;
            }
            if (iVar8 < *(int *)(uVar11 + 0x1c)) {
              *(int *)(uVar11 + 0x1c) = iVar8;
              *(uint *)(uVar11 + 0x14) = uVar10;
            }
          }
        }
      }
    }
  }
  for (; uVar5 < uVar7; uVar5 = uVar5 + 0x2c) {
    iVar1 = *(int *)(uVar5 + 0x14);
    if ((iVar1 != 0) && (*(uint *)(iVar1 + 0x14) != uVar5)) {
      *(undefined4 *)(uVar5 + 0x14) = 0;
      *(undefined4 *)(uVar5 + 0x18) = *(undefined4 *)(iVar1 + 0x14);
    }
  }
  return;
}

