
void FUN_00523674(undefined4 param_1,undefined4 param_2,float param_3,float param_4,float param_5,
                 float param_6,int param_7)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  undefined4 *puVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  bool bVar16;
  bool bVar17;
  uint in_fpscr;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  int iVar23;
  float fVar24;
  float fVar25;
  
  fVar18 = param_3;
  if (param_3 < 1.0) {
    fVar18 = 1.0;
  }
  if (param_4 < 1.0) {
    param_4 = 1.0;
  }
  param_4 = param_4 * 0.5;
  if (!NAN(param_4 + 0.5) && !NAN(param_3)) {
    fVar18 = param_4;
  }
  if (param_5 != param_6) {
    iVar23 = (int)(fVar18 * DAT_00523a20 + 0.5);
    uVar7 = DAT_00523a24;
    if ((iVar23 < 0x61) && (uVar7 = DAT_00523a28, 0x1f < iVar23)) {
      uVar7 = iVar23 + 0xf + ((uint)(iVar23 + 0xf >> 3) >> 0x1c) & 0xfffffff0;
    }
    fVar22 = param_6 - param_5;
    if (fVar22 < 0.0) {
      fVar22 = param_5 - param_6;
    }
    fVar21 = (float)VectorSignedToFloat(uVar7,(byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
    fVar21 = (fVar21 * fVar22) / DAT_00523a2c;
    fVar24 = (float)VectorSignedToFloat((int)fVar21,(byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
    fVar25 = fVar18 + param_4;
    fVar18 = fVar18 - param_4;
    iVar15 = (uint)((int)((uint)(fVar24 < fVar21) << 0x1f) < 0) + (int)fVar21;
    iVar23 = 0;
    fVar22 = fVar22 / fVar21;
    fVar21 = param_5;
    if (param_5 <= param_6) {
      do {
        fVar21 = fVar21 + fVar22;
        bVar16 = param_6 < fVar21;
        bVar17 = NAN(param_6) || NAN(fVar21);
        iVar4 = iVar23 + 9;
        if (!bVar16) {
          fVar21 = fVar21 + fVar22;
          bVar16 = param_6 < fVar21;
          bVar17 = NAN(param_6) || NAN(fVar21);
          iVar4 = iVar23 + 0x12;
        }
        iVar23 = iVar4;
        if (bVar16 != bVar17) break;
        fVar21 = fVar21 + fVar22;
        bVar16 = param_6 < fVar21;
        bVar17 = NAN(param_6) || NAN(fVar21);
        iVar4 = iVar23 + 9;
        if (!bVar16) {
          fVar21 = fVar21 + fVar22;
          bVar16 = param_6 < fVar21;
          bVar17 = NAN(param_6) || NAN(fVar21);
          iVar4 = iVar23 + 0x12;
        }
        iVar23 = iVar4;
      } while (bVar16 == bVar17);
    }
    iVar23 = FUN_00514d2c(iVar23);
    if (-1 < iVar23) {
      fVar21 = (float)FUN_00524130(param_5);
      fVar24 = (float)FUN_0052405c(param_5);
      fVar19 = (float)FUN_00524130(param_5);
      fVar20 = (float)FUN_0052405c(param_5);
      iVar2 = FUN_005242cc(param_1);
      iVar3 = FUN_005242cc(param_2);
      iVar23 = FUN_005242cc(fVar25 * fVar21);
      iVar4 = FUN_005242cc(fVar25 * fVar24);
      iVar5 = FUN_005242cc(fVar18 * fVar19);
      iVar6 = FUN_005242cc(fVar18 * fVar20);
      iVar13 = *DAT_00523bf0;
      uVar14 = *(uint *)(iVar13 + 0x1c);
      *(undefined4 *)(iVar13 + 0x1c) = 0x2800000;
      uVar7 = *(uint *)(iVar13 + 0x10) | *(uint *)(iVar13 + 0xc) | *(uint *)(iVar13 + 0x14);
      *(uint *)(iVar13 + 0x18) = uVar7 | 0x2800000;
      if (param_7 << 5 < 0) {
        *(undefined4 *)(iVar13 + 0x1c) = 0x6800000;
        *(uint *)(iVar13 + 0x18) = uVar7 | 0x6800000;
      }
      if (0 < iVar15) {
        iVar13 = 0;
        do {
          param_5 = param_5 + fVar22;
          if (iVar13 + 1 == iVar15) {
            if (param_7 << 7 < 0) {
              if ((param_7 << 5 < 0) && (iVar15 == 1)) {
                iVar8 = *DAT_00523bf0;
                *(undefined4 *)(iVar8 + 0x1c) = 0x7800000;
                uVar7 = *(uint *)(iVar8 + 0xc) | *(uint *)(iVar8 + 0x14) | *(uint *)(iVar8 + 0x10) |
                        0x7800000;
              }
              else {
                iVar8 = *DAT_00523bf0;
                *(undefined4 *)(iVar8 + 0x1c) = 0x3800000;
                uVar7 = *(uint *)(iVar8 + 0xc) | *(uint *)(iVar8 + 0x14) | *(uint *)(iVar8 + 0x10) |
                        0x3800000;
              }
              *(uint *)(iVar8 + 0x18) = uVar7;
            }
            fVar20 = (float)FUN_00524130(param_6);
            fVar19 = (float)FUN_00524130(param_6);
            fVar24 = (float)FUN_0052405c(param_6);
            fVar21 = param_6;
          }
          else {
            fVar20 = (float)FUN_00524130(param_5);
            fVar19 = (float)FUN_00524130(param_5);
            fVar24 = (float)FUN_0052405c(param_5);
            fVar21 = param_5;
          }
          fVar21 = (float)FUN_0052405c(fVar21);
          iVar8 = FUN_005242cc(fVar20 * fVar25);
          iVar9 = FUN_005242cc(fVar24 * fVar25);
          iVar10 = FUN_005242cc(fVar19 * fVar18);
          iVar11 = FUN_005242cc(fVar21 * fVar18);
          puVar12 = (undefined4 *)FUN_00514aec(9);
          piVar1 = DAT_00523bf0;
          if (puVar12 != (undefined4 *)0x0) {
            *puVar12 = 0x120;
            puVar12[2] = 0x124;
            puVar12[1] = iVar5 + iVar2;
            puVar12[4] = 0x130;
            puVar12[3] = iVar6 + iVar3;
            puVar12[6] = 0x134;
            puVar12[5] = iVar23 + iVar2;
            puVar12[8] = 0x140;
            puVar12[7] = iVar4 + iVar3;
            puVar12[9] = iVar8 + iVar2;
            puVar12[10] = 0x144;
            puVar12[0xc] = 0x150;
            puVar12[0xb] = iVar9 + iVar3;
            puVar12[0xe] = 0x154;
            puVar12[0xd] = iVar2 + iVar10;
            puVar12[0x10] = DAT_00523a30;
            puVar12[0xf] = iVar3 + iVar11;
            puVar12[0x11] = *(uint *)(*piVar1 + 0x18) | 5;
          }
          iVar23 = *piVar1;
          *(undefined4 *)(iVar23 + 0x1c) = 0x2800000;
          iVar13 = iVar13 + 1;
          *(uint *)(iVar23 + 0x18) =
               *(uint *)(iVar23 + 0xc) | *(uint *)(iVar23 + 0x14) | *(uint *)(iVar23 + 0x10) |
               0x2800000;
          iVar23 = iVar8;
          iVar4 = iVar9;
          iVar5 = iVar10;
          iVar6 = iVar11;
        } while (iVar13 < iVar15);
      }
      iVar23 = *DAT_00523bf0;
      uVar14 = uVar14 & 0x7800000;
      *(uint *)(iVar23 + 0x1c) = uVar14;
      *(uint *)(iVar23 + 0x18) =
           uVar14 | *(uint *)(iVar23 + 0xc) | *(uint *)(iVar23 + 0x14) | *(uint *)(iVar23 + 0x10);
    }
  }
  return;
}

