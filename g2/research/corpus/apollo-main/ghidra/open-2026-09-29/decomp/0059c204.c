
void FUN_0059c204(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6,
                 float *param_7)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  uint extraout_r1;
  uint extraout_r1_00;
  undefined4 extraout_r1_01;
  undefined4 extraout_r1_02;
  undefined4 extraout_r1_03;
  undefined4 uVar7;
  float *pfVar8;
  int iVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  float *pfVar13;
  uint uVar14;
  uint uVar15;
  uint uVar16;
  int iVar17;
  uint uVar18;
  uint in_fpscr;
  float fVar19;
  uint uVar20;
  float fVar21;
  uint uVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  int local_58;
  uint local_54;
  
  iVar9 = DAT_0059c7a0;
  uVar11 = (uint)*(byte *)(param_6 + 8);
  uVar10 = *(uint *)(param_6 + 4);
  if (param_4 < 4) {
    param_4 = param_4 << 2;
  }
  else {
    param_4 = 0x10;
  }
  iVar1 = param_2 + 1;
  uVar16 = iVar1 * *(int *)(DAT_0059c7a0 + param_4);
  if (param_2 < 2) {
    iVar2 = 0;
LAB_0059c254:
    iVar4 = 0;
  }
  else {
    iVar2 = 1;
    if (param_2 < 3) goto LAB_0059c254;
    iVar4 = 1;
  }
  iVar2 = iVar2 + iVar4 + 1;
  if (4 < param_3) {
    fVar19 = 0.5;
  }
  else {
    fVar19 = 0.625;
  }
  iVar17 = iVar1 * 6 - iVar2;
  iVar4 = 0;
  iVar5 = 0;
  pfVar13 = param_7 + iVar17;
  pfVar8 = param_7 + (iVar17 - iVar2);
  fVar23 = DAT_0059c3b0;
  while( true ) {
    uVar15 = uVar10;
    if ((int)uVar16 < (int)uVar10) {
      uVar15 = uVar16;
    }
    if ((int)uVar15 <= iVar17) break;
    in_fpscr = in_fpscr & 0xfffffff;
    if (fVar19 <= ABS(*pfVar13)) {
      iVar5 = 0;
    }
    else {
      iVar5 = iVar5 + 1;
    }
    if (iVar2 * 2 < iVar5) {
      fVar23 = ABS(*pfVar8) + fVar23;
      iVar4 = iVar4 + 1;
    }
    iVar17 = iVar17 + 1;
    pfVar8 = pfVar8 + 1;
    pfVar13 = pfVar13 + 1;
  }
  if (iVar17 < (int)(iVar2 + uVar16)) {
    do {
      loopEnd();
    } while( true );
  }
  if (iVar4 != 0) {
    fVar19 = (float)VectorSignedToFloat(iVar4,(byte)(in_fpscr >> 0x16) & 3);
    iVar2 = 8 - (int)((fVar23 * 16.0) / fVar19 + 0.5);
    if (iVar2 < 1) {
      iVar2 = 0;
      goto LAB_0059c33a;
    }
    if (iVar2 < 8) goto LAB_0059c33a;
  }
  iVar2 = 7;
LAB_0059c33a:
  FUN_0059b6ac(param_1,iVar2,3);
  iVar2 = param_3;
  if (4 < param_3) {
    iVar2 = param_3 + -1;
  }
  if (((iVar2 + 1) * 0x14 < param_5) && (param_3 < 6)) {
    iVar2 = 0x800;
  }
  else {
    iVar2 = 0;
  }
  iVar9 = *(int *)(iVar9 + param_3 * 4);
  local_54 = 0;
  uVar16 = 0;
  uVar18 = DAT_0059c7a4 + iVar2;
  fVar19 = 0.5;
  local_58 = 0;
  do {
    pfVar8 = param_7 + local_54;
    uVar3 = iVar9 * iVar1 + 2 >> (1U - local_58 & 0xff);
    while( true ) {
      uVar14 = uVar10;
      if ((int)uVar3 <= (int)uVar10) {
        uVar14 = uVar3;
      }
      if ((int)uVar14 <= (int)local_54) break;
      fVar23 = 0.375;
      if (4 < param_3) {
        fVar23 = 0.5;
      }
      uVar22 = (uint)(0.0 < ABS(*pfVar8) + fVar23) * (int)(ABS(*pfVar8) + fVar23);
      uVar20 = (uint)(0.0 < ABS(pfVar8[1]) + fVar23) * (int)(ABS(pfVar8[1]) + fVar23);
      uVar12 = 0;
      uVar14 = (uVar20 | uVar22) >> 2;
      uVar15 = 0;
      uVar6 = local_54;
      if (uVar14 != 0) {
        if (uVar11 != 0) {
          iVar2 = DAT_0059c7a8 + (uint)*(byte *)(uVar18 + uVar16 * 4) * 0x44;
          uVar15 = *(uint *)(param_1 + 8) >> 10;
          uVar12 = *(ushort *)(iVar2 + 0x40) * uVar15 + *(int *)(param_1 + 4);
          uVar15 = *(ushort *)(iVar2 + 0x42) * uVar15;
          *(uint *)(param_1 + 8) = uVar15;
          *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) | uVar12 >> 0x18;
          *(uint *)(param_1 + 4) = uVar12 & 0xffffff;
          if (uVar15 < 0x10000) {
            FUN_00439b54(param_1);
          }
          uVar12 = 1;
        }
        iVar2 = DAT_0059c7a8;
        uVar6 = uVar18;
        for (uVar14 = uVar14 >> uVar11; uVar14 != 0; uVar14 = uVar14 >> 1) {
          FUN_0059b6ac(param_1,uVar22 >> (uVar12 & 0xff) & 1,1);
          FUN_0059b6ac(param_1,uVar20 >> (uVar12 & 0xff) & 1,1);
          uVar15 = uVar12;
          if (2 < uVar12) {
            uVar15 = 3;
          }
          iVar4 = iVar2 + (uint)*(byte *)(uVar18 + uVar16 * 4 + uVar15) * 0x44;
          uVar6 = *(uint *)(param_1 + 8) >> 10;
          uVar15 = *(ushort *)(iVar4 + 0x40) * uVar6 + *(int *)(param_1 + 4);
          uVar6 = *(ushort *)(iVar4 + 0x42) * uVar6;
          *(uint *)(param_1 + 8) = uVar6;
          *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) | uVar15 >> 0x18;
          *(uint *)(param_1 + 4) = uVar15 & 0xffffff;
          if (uVar6 < 0x10000) {
            FUN_00439b54(param_1);
            uVar6 = extraout_r1;
          }
          uVar12 = uVar12 + 1;
        }
        uVar22 = uVar22 >> uVar11;
        uVar20 = uVar20 >> uVar11;
        uVar15 = uVar12 - uVar11;
        if (2 < uVar12) {
          uVar12 = 3;
        }
      }
      if (uVar22 != 0) {
        iVar2 = (uint)(*pfVar8 < 0.0) << 0x1f;
        if (iVar2 < 0) {
          uVar6 = 1;
        }
        if (-1 < iVar2) {
          uVar6 = 0;
        }
        FUN_0059b6ac(param_1,uVar6,1);
        uVar6 = extraout_r1_00;
      }
      if (uVar20 != 0) {
        iVar2 = (uint)(pfVar8[1] < 0.0) << 0x1f;
        if (iVar2 < 0) {
          uVar6 = 1;
        }
        if (-1 < iVar2) {
          uVar6 = 0;
        }
        FUN_0059b6ac(param_1,uVar6,1);
      }
      uVar22 = uVar22 >> (uVar15 & 0xff);
      uVar20 = uVar20 >> (uVar15 & 0xff);
      iVar4 = uVar22 + uVar20 * 4;
      iVar2 = DAT_0059c7a8 + (uint)*(byte *)(uVar18 + uVar16 * 4 + uVar12) * 0x44;
      uVar14 = *(uint *)(param_1 + 8) >> 10;
      uVar6 = *(ushort *)(iVar2 + iVar4 * 4) * uVar14 + *(int *)(param_1 + 4);
      uVar14 = *(ushort *)(iVar2 + iVar4 * 4 + 2) * uVar14;
      *(uint *)(param_1 + 8) = uVar14;
      *(uint *)(param_1 + 0x10) = *(uint *)(param_1 + 0x10) | uVar6 >> 0x18;
      *(uint *)(param_1 + 4) = uVar6 & 0xffffff;
      if (uVar14 < 0x10000) {
        FUN_00439b54(param_1);
      }
      if (uVar12 < 2) {
        iVar2 = (uVar12 + 1) * (uVar20 + uVar22) + 1;
      }
      else {
        iVar2 = uVar12 + 0xc;
      }
      pfVar8 = pfVar8 + 2;
      local_54 = local_54 + 2;
      uVar16 = iVar2 + uVar16 * 0x10 & 0xff;
    }
    local_58 = local_58 + 1;
    uVar18 = uVar18 + 0x400;
  } while (local_58 < 2);
  iVar9 = FUN_00439914(param_1);
  if (uVar11 == 0) {
    if (4 >= param_3) {
      fVar19 = 0.625;
    }
    fVar23 = fVar19 * 0.5;
    iVar1 = 0;
    while( true ) {
      if (4 < param_3) {
        iVar2 = 0x14;
      }
      else {
        iVar2 = 1;
      }
      if ((iVar2 <= iVar1) || (iVar9 < 1)) break;
      if (0 < (int)uVar10) {
        uVar11 = uVar10;
        pfVar8 = param_7;
        do {
          fVar24 = *pfVar8;
          fVar25 = ABS(fVar24);
          if (-1 < (int)((uint)(fVar25 < fVar19) << 0x1f)) {
            fVar21 = (float)FUN_0059f510(fVar25);
            iVar2 = (uint)(fVar25 - fVar21 < fVar19) << 0x1f;
            if (iVar2 < 0) {
              uVar15 = 1;
            }
            if (-1 < iVar2) {
              uVar15 = 0;
            }
            if ((int)((uint)(fVar24 < 0.0) << 0x1f) < 0) {
              uVar15 = uVar15 ^ 1;
            }
            FUN_0059b6ac(param_1,uVar15 & 0xff,1);
            iVar9 = iVar9 + -1;
            fVar24 = -fVar23;
            if (uVar15 == 0) {
              fVar24 = fVar23;
            }
            *pfVar8 = *pfVar8 + fVar24;
          }
          pfVar8 = pfVar8 + 1;
          uVar11 = uVar11 - 1;
        } while ((uVar11 != 0) && (0 < iVar9));
      }
      fVar23 = fVar23 * fVar19;
      iVar1 = iVar1 + 1;
    }
  }
  else {
    iVar1 = 0;
    if (0 < (int)uVar10) {
      while (0 < iVar9) {
        fVar19 = 0.5;
        if (4 >= param_3) {
          fVar19 = 0.375;
        }
        uVar16 = (uint)(0.0 < ABS(*param_7) + fVar19) * (int)(ABS(*param_7) + fVar19);
        uVar11 = (uint)(0.0 < ABS(param_7[1]) + fVar19) * (int)(ABS(param_7[1]) + fVar19);
        if ((uVar11 | uVar16) >> 2 != 0) {
          FUN_0059b6ac(param_1,uVar16 & 1,1);
          uVar7 = extraout_r1_01;
          iVar2 = iVar9 + -1;
          if ((uVar16 == 1) && (iVar2 = iVar9 + -2, 0 < iVar9 + -1)) {
            iVar9 = (uint)(*param_7 < 0.0) << 0x1f;
            if (iVar9 < 0) {
              uVar7 = 1;
            }
            if (-1 < iVar9) {
              uVar7 = 0;
            }
            FUN_0059b6ac(param_1,uVar7,1);
            uVar7 = extraout_r1_02;
          }
          if (0 < iVar2) {
            FUN_0059b6ac(param_1,uVar11 & 1,1);
            uVar7 = extraout_r1_03;
          }
          iVar9 = iVar2 + -1;
          if ((uVar11 == 1) && (iVar9 = iVar2 + -2, 0 < iVar2 + -1)) {
            iVar2 = (uint)(param_7[1] < 0.0) << 0x1f;
            if (iVar2 < 0) {
              uVar7 = 1;
            }
            if (-1 < iVar2) {
              uVar7 = 0;
            }
            FUN_0059b6ac(param_1,uVar7,1);
          }
        }
        iVar1 = iVar1 + 2;
        param_7 = param_7 + 2;
        if ((int)uVar10 <= iVar1) {
          return;
        }
      }
    }
  }
  return;
}

