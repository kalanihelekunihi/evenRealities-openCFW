
void FUN_0052330c(undefined4 param_1,undefined4 param_2,float param_3,float param_4,float param_5,
                 float param_6)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  undefined4 *puVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  bool bVar14;
  bool bVar15;
  uint in_fpscr;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  int iVar21;
  float fVar22;
  float fVar23;
  
  fVar16 = param_3;
  if (param_3 < 1.0) {
    fVar16 = 1.0;
  }
  if (param_4 < 1.0) {
    param_4 = 1.0;
  }
  param_4 = param_4 * 0.5;
  if (!NAN(param_4 + 0.5) && !NAN(param_3)) {
    fVar16 = param_4;
  }
  if (param_5 != param_6) {
    iVar21 = (int)(fVar16 * DAT_00523664 + 0.5);
    uVar10 = DAT_00523668;
    if ((iVar21 < 0x61) && (uVar10 = DAT_0052366c, 0x1f < iVar21)) {
      uVar10 = iVar21 + 0xf + ((uint)(iVar21 + 0xf >> 3) >> 0x1c) & 0xfffffff0;
    }
    fVar20 = param_6 - param_5;
    if (fVar20 < 0.0) {
      fVar20 = param_5 - param_6;
    }
    fVar19 = (float)VectorSignedToFloat(uVar10,(byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
    fVar19 = (fVar19 * fVar20) / DAT_00523670;
    fVar22 = (float)VectorSignedToFloat((int)fVar19,(byte)((in_fpscr & 0xfffffff) >> 0x16) & 3);
    fVar23 = fVar16 + param_4;
    fVar16 = fVar16 - param_4;
    iVar13 = (uint)((int)((uint)(fVar22 < fVar19) << 0x1f) < 0) + (int)fVar19;
    iVar21 = 0;
    fVar20 = fVar20 / fVar19;
    fVar19 = param_5;
    if (param_5 <= param_6) {
      do {
        fVar19 = fVar19 + fVar20;
        bVar14 = param_6 < fVar19;
        bVar15 = NAN(param_6) || NAN(fVar19);
        iVar3 = iVar21 + 9;
        if (!bVar14) {
          fVar19 = fVar19 + fVar20;
          bVar14 = param_6 < fVar19;
          bVar15 = NAN(param_6) || NAN(fVar19);
          iVar3 = iVar21 + 0x12;
        }
        iVar21 = iVar3;
        if (bVar14 != bVar15) break;
        fVar19 = fVar19 + fVar20;
        bVar14 = param_6 < fVar19;
        bVar15 = NAN(param_6) || NAN(fVar19);
        iVar3 = iVar21 + 9;
        if (!bVar14) {
          fVar19 = fVar19 + fVar20;
          bVar14 = param_6 < fVar19;
          bVar15 = NAN(param_6) || NAN(fVar19);
          iVar3 = iVar21 + 0x12;
        }
        iVar21 = iVar3;
      } while (bVar14 == bVar15);
    }
    iVar21 = FUN_00514d2c(iVar21);
    if (-1 < iVar21) {
      fVar19 = (float)FUN_00524130(param_5);
      fVar22 = (float)FUN_0052405c(param_5);
      fVar17 = (float)FUN_00524130(param_5);
      fVar18 = (float)FUN_0052405c(param_5);
      iVar1 = FUN_005242cc(param_1);
      iVar2 = FUN_005242cc(param_2);
      iVar3 = FUN_005242cc(fVar23 * fVar19);
      iVar4 = FUN_005242cc(fVar23 * fVar22);
      iVar5 = FUN_005242cc(fVar16 * fVar17);
      iVar21 = FUN_005242cc(fVar16 * fVar18);
      iVar11 = *DAT_00523bf0;
      iVar12 = 0;
      uVar10 = *(uint *)(iVar11 + 0x1c);
      *(undefined4 *)(iVar11 + 0x1c) = 0x2800000;
      *(uint *)(iVar11 + 0x18) =
           *(uint *)(iVar11 + 0x10) | *(uint *)(iVar11 + 0x14) | *(uint *)(iVar11 + 0xc) | 0x2800000
      ;
      if (0 < iVar13) {
        do {
          param_5 = param_5 + fVar20;
          if (iVar12 + 1 == iVar13) {
            fVar18 = (float)FUN_00524130(param_6);
            fVar17 = (float)FUN_00524130(param_6);
            fVar22 = (float)FUN_0052405c(param_6);
            fVar19 = param_6;
          }
          else {
            fVar18 = (float)FUN_00524130(param_5);
            fVar17 = (float)FUN_00524130(param_5);
            fVar22 = (float)FUN_0052405c(param_5);
            fVar19 = param_5;
          }
          fVar19 = (float)FUN_0052405c(fVar19);
          iVar11 = FUN_005242cc(fVar18 * fVar23);
          iVar6 = FUN_005242cc(fVar22 * fVar23);
          iVar7 = FUN_005242cc(fVar17 * fVar16);
          iVar8 = FUN_005242cc(fVar19 * fVar16);
          puVar9 = (undefined4 *)FUN_00514aec(9);
          if (puVar9 != (undefined4 *)0x0) {
            *puVar9 = 0x120;
            puVar9[2] = 0x124;
            puVar9[1] = iVar5 + iVar1;
            puVar9[4] = 0x130;
            puVar9[3] = iVar21 + iVar2;
            puVar9[6] = 0x134;
            puVar9[5] = iVar3 + iVar1;
            puVar9[8] = 0x140;
            puVar9[7] = iVar4 + iVar2;
            puVar9[9] = iVar11 + iVar1;
            puVar9[10] = 0x144;
            puVar9[0xc] = 0x150;
            puVar9[0xb] = iVar2 + iVar6;
            puVar9[0xe] = 0x154;
            puVar9[0xd] = iVar7 + iVar1;
            puVar9[0x10] = DAT_00523a30;
            puVar9[0xf] = iVar2 + iVar8;
            puVar9[0x11] = *(uint *)(*DAT_00523bf0 + 0x18) | 5;
          }
          iVar21 = *DAT_00523bf0;
          *(undefined4 *)(iVar21 + 0x1c) = 0x2800000;
          iVar12 = iVar12 + 1;
          *(uint *)(iVar21 + 0x18) =
               *(uint *)(iVar21 + 0xc) | *(uint *)(iVar21 + 0x14) | *(uint *)(iVar21 + 0x10) |
               0x2800000;
          iVar21 = iVar8;
          iVar3 = iVar11;
          iVar5 = iVar7;
          iVar4 = iVar6;
        } while (iVar12 < iVar13);
      }
      iVar21 = *DAT_00523bf0;
      uVar10 = uVar10 & 0x7800000;
      *(uint *)(iVar21 + 0x1c) = uVar10;
      *(uint *)(iVar21 + 0x18) =
           uVar10 | *(uint *)(iVar21 + 0xc) | *(uint *)(iVar21 + 0x14) | *(uint *)(iVar21 + 0x10);
    }
  }
  return;
}

