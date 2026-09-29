
ushort * af_glyph_hints_align_strong_points(int param_1,byte param_2)

{
  ushort uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  ushort *puVar5;
  int iVar6;
  int iVar7;
  short *psVar8;
  short *psVar9;
  ushort uVar10;
  ushort *puVar11;
  int iVar12;
  
  puVar11 = *(ushort **)(param_1 + 0x1c);
  puVar5 = puVar11 + *(int *)(param_1 + 0x18) * 0x14;
  param_1 = param_1 + (uint)param_2 * 0x544;
  psVar8 = *(short **)(param_1 + 0x40);
  psVar9 = psVar8 + *(int *)(param_1 + 0x38) * 0x16;
  if (param_2 == 0) {
    uVar10 = 4;
  }
  else {
    uVar10 = 8;
  }
  if (psVar8 < psVar9) {
    for (; puVar11 < puVar5; puVar11 = puVar11 + 0x14) {
      if (((*puVar11 & uVar10) == 0) && (-1 < (int)((uint)(byte)*puVar11 << 0x1b))) {
        if (param_2 == 1) {
          uVar1 = puVar11[7];
          iVar2 = *(int *)(puVar11 + 4);
        }
        else {
          uVar1 = puVar11[6];
          iVar2 = *(int *)(puVar11 + 2);
        }
        iVar6 = (int)(short)uVar1;
        if (*psVar8 - iVar6 < 0) {
          if (iVar6 - psVar9[-0x16] < 0) {
            iVar3 = 0;
            iVar2 = ((int)psVar9 - (int)psVar8) / 0x2c;
            if (iVar2 < 9) {
              iVar3 = 0;
              while ((iVar3 < iVar2 && (psVar8[iVar3 * 0x16] < iVar6))) {
                iVar3 = iVar3 + 1;
              }
              if (psVar8[iVar3 * 0x16] == iVar6) {
                iVar2 = *(int *)(psVar8 + iVar3 * 0x16 + 4);
                goto LAB_005a86c4;
              }
            }
            else {
              while (iVar7 = iVar2, iVar3 < iVar7) {
                iVar2 = iVar3 + iVar7 >> 1;
                iVar12 = (int)psVar8[iVar2 * 0x16];
                if (iVar12 <= iVar6) {
                  if (iVar6 <= iVar12) {
                    iVar2 = *(int *)(psVar8 + iVar2 * 0x16 + 4);
                    goto LAB_005a86c4;
                  }
                  iVar3 = iVar2 + 1;
                  iVar2 = iVar7;
                }
              }
            }
            if (*(int *)(psVar8 + iVar3 * 0x16 + -0xe) == 0) {
              uVar4 = FT_DivFix(*(int *)(psVar8 + iVar3 * 0x16 + 4) -
                                *(int *)(psVar8 + iVar3 * 0x16 + -0x12),
                                (int)psVar8[iVar3 * 0x16] - (int)psVar8[iVar3 * 0x16 + -0x16]);
              *(undefined4 *)(psVar8 + iVar3 * 0x16 + -0xe) = uVar4;
            }
            iVar2 = FT_MulFix(iVar6 - psVar8[iVar3 * 0x16 + -0x16],
                              *(undefined4 *)(psVar8 + iVar3 * 0x16 + -0xe));
            iVar2 = iVar2 + *(int *)(psVar8 + iVar3 * 0x16 + -0x12);
          }
          else {
            iVar2 = (iVar2 + *(int *)(psVar9 + -0x12)) - *(int *)(psVar9 + -0x14);
          }
        }
        else {
          iVar2 = iVar2 + (*(int *)(psVar8 + 4) - *(int *)(psVar8 + 2));
        }
LAB_005a86c4:
        if (param_2 == 0) {
          *(int *)(puVar11 + 8) = iVar2;
        }
        else {
          *(int *)(puVar11 + 10) = iVar2;
        }
        *puVar11 = uVar10 | *puVar11;
      }
    }
  }
  return puVar5;
}

