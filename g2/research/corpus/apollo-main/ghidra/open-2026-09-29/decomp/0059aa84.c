
/* WARNING: Instruction at (ram,0x0059ad7e) overlaps instruction at (ram,0x0059ad7c)
    */
/* WARNING: Type propagation algorithm not settling */

void FUN_0059aa84(uint param_1,float param_2,char param_3,int param_4,int *param_5,int param_6)

{
  bool bVar1;
  bool bVar2;
  int iVar3;
  float *pfVar4;
  float ****ppppfVar5;
  undefined1 **ppuVar6;
  int iVar7;
  float *pfVar8;
  float *pfVar9;
  float ******ppppppfVar10;
  float *pfVar11;
  float ****ppppfVar12;
  float ****ppppfVar13;
  int *piVar14;
  uint uVar15;
  uint uVar16;
  int iVar17;
  int iVar18;
  int iVar19;
  int iVar20;
  int iVar21;
  int iVar22;
  int *piVar23;
  float *pfVar24;
  undefined1 **ppuVar25;
  float ****ppppfVar26;
  int iVar27;
  uint in_fpscr;
  undefined4 uVar28;
  float ****ppppfVar29;
  float fVar30;
  float ***pppfVar31;
  float ***extraout_s1;
  float fVar32;
  float fVar33;
  float ***pppfVar34;
  float fVar35;
  undefined1 *puVar36;
  float fVar37;
  float local_1c8;
  float ****local_1c4;
  float ******local_1c0;
  float ****local_1bc [2];
  float *local_1b4;
  float *local_1b0;
  float *****local_1ac;
  float local_1a8 [19];
  float ******local_15c;
  undefined1 *local_158 [7];
  float afStack_13c [17];
  float ***local_f8 [7];
  float ***local_dc [11];
  float local_b0;
  float local_ac;
  float local_a8;
  float local_a4 [25];
  char local_2c;
  
  local_1a8[0] = (float)(param_1 + 1);
  *(bool *)(param_5 + 1) = param_4 * 8 < (int)local_1a8[0] * 0x78;
  local_2c = (char)param_1;
  if (((param_1 & 0xff) == 0) || ((int)param_2 < 3)) {
    iVar3 = 1;
  }
  else {
    iVar3 = 2;
  }
  *param_5 = iVar3;
  if ((int)param_1 < 2) {
    ppppfVar13 = (float ****)&Reset;
  }
  else {
    ppppfVar13 = (float ****)&NMI;
  }
  piVar14 = *(int **)(DAT_0059b5c0 + param_1 * 0x1c + (int)param_2 * 4 + 0x6c);
  if ((local_2c == '\0') || ((int)param_2 < 3)) {
    local_1b4 = (float *)0x1;
  }
  else {
    local_1b4 = (float *)0x2;
  }
  uVar28 = DAT_0059acb4;
  if ((int)param_1 < 2) {
    uVar28 = DAT_0059acb8;
  }
  iVar3 = param_6 + *piVar14 * 4;
  local_1c4 = (float ****)local_1b4;
  local_1c8 = param_2;
  local_1b0 = (float *)FUN_0048949c(uVar28,&local_b0,0x6c);
  pppfVar31 = (float ***)VectorSignedToFloat(local_1b0,(byte)(in_fpscr >> 0x16) & 3);
  local_1c0 = (float ******)local_f8;
  while( true ) {
    fVar32 = DAT_0059b308;
    fVar30 = DAT_0059b304;
    fVar33 = DAT_0059b300;
    pfVar8 = &local_b0;
    pfVar4 = local_1b0;
    iVar22 = iVar3;
    do {
      piVar14 = piVar14 + 1;
      iVar18 = 0;
      iVar3 = param_6 + *piVar14 * 4;
      iVar22 = iVar3 - iVar22 >> 2;
      pfVar9 = pfVar8;
      do {
        if (iVar22 != 0) {
          do {
            loopEnd();
          } while( true );
        }
        *pfVar9 = (float)DAT_0059acbc;
        iVar18 = iVar18 + 1;
        iVar22 = -1;
        pfVar9 = pfVar9 + 3;
      } while (iVar18 <= (int)ppppfVar13);
      pfVar8 = pfVar8 + 1;
      pfVar4 = (float *)((int)pfVar4 + -1);
      iVar22 = iVar3;
    } while (pfVar4 != (float *)0x0);
    *local_1c0 = (float *****)pppfVar31;
    if (local_1b0 == (float *)0x2) {
      iVar22 = 1;
      pfVar8 = (float *)(DAT_0059b5c0 + 0xe0);
      pfVar4 = local_a4;
      ppppppfVar10 = local_1c0;
      do {
        ppppppfVar10 = ppppppfVar10 + 1;
        pppfVar31 = DAT_0059acbc;
        if (local_b0 != 0.0 && (local_b0 != 0.0 && local_ac != 0.0)) {
          pppfVar31 = (float ***)((*pfVar4 / local_b0 + pfVar4[1] / local_ac) * *pfVar8);
        }
        *ppppppfVar10 = (float *****)pppfVar31;
        iVar22 = iVar22 + 1;
        pfVar4 = pfVar4 + 3;
        pfVar8 = pfVar8 + 1;
      } while (iVar22 <= (int)ppppfVar13);
    }
    else {
      iVar22 = 1;
      pfVar4 = (float *)(DAT_0059b5c0 + 0xe0);
      pfVar8 = local_a4;
      ppppppfVar10 = local_1c0;
      do {
        ppppppfVar10 = ppppppfVar10 + 1;
        bVar1 = local_b0 == 0.0;
        bVar2 = bVar1 || (bVar1 || local_ac == 0.0);
        if (!bVar1 && (!bVar1 && local_ac != 0.0)) {
          bVar2 = local_a8 == 0.0;
        }
        pppfVar31 = DAT_0059acbc;
        if (!bVar2) {
          pppfVar31 = (float ***)
                      ((*pfVar8 / local_b0 + pfVar8[1] / local_ac + pfVar8[2] / local_a8) * *pfVar4)
          ;
        }
        *ppppppfVar10 = (float *****)pppfVar31;
        iVar22 = iVar22 + 1;
        pfVar8 = pfVar8 + 3;
        pfVar4 = pfVar4 + 1;
      } while (iVar22 <= (int)ppppfVar13);
    }
    local_1c0 = local_1c0 + 9;
    local_1c4 = (float ****)((int)local_1c4 + -1);
    if (local_1c4 == (float ****)0x0) break;
    FUN_00439c04(&local_b0,DAT_0059b5c0,0x6c);
    pppfVar31 = extraout_s1;
  }
  pfVar4 = (float *)local_1bc;
  ppppfVar29 = local_f8;
  pfVar8 = &local_1c8;
  do {
    pfVar11 = pfVar8 + 9;
    ppppfVar5 = ppppfVar29 + 1;
    pppfVar34 = *ppppfVar29;
    *pfVar11 = 1.0;
    ppuVar6 = local_158;
    fVar35 = -(float)*ppppfVar5;
    pfVar9 = pfVar11;
    uVar16 = 1;
    pppfVar31 = pppfVar34;
    while( true ) {
      uVar15 = uVar16;
      puVar36 = (undefined1 *)(fVar35 / (float)pppfVar31);
      fVar35 = (1.0 - (float)puVar36 * (float)puVar36) * (float)pppfVar31;
      if (1 < (int)uVar15) {
        local_1c4 = (float ****)(uVar15 - 1);
        ppuVar25 = local_158;
        pfVar24 = pfVar8 + 10;
        if (((uint)local_1c4 & 3) != 0) {
          do {
            *ppuVar25 = (undefined1 *)(*pfVar24 + (float)puVar36 * *pfVar9);
            pfVar24 = pfVar24 + 1;
            ppuVar25 = ppuVar25 + 1;
            pfVar9 = pfVar9 + -1;
            loopEnd();
          } while( true );
        }
        if ((uint)local_1c4 >> 2 != 0) {
          do {
            *ppuVar25 = (undefined1 *)(*pfVar24 + (float)puVar36 * *pfVar9);
            ppuVar25[1] = (undefined1 *)(pfVar24[1] + (float)puVar36 * pfVar9[-1]);
            ppuVar25[2] = (undefined1 *)(pfVar24[2] + (float)puVar36 * pfVar9[-2]);
            ppuVar25[3] = (undefined1 *)(pfVar24[3] + (float)puVar36 * pfVar9[-3]);
            pfVar24 = pfVar24 + 4;
            ppuVar25 = ppuVar25 + 4;
            pfVar9 = pfVar9 + -4;
            loopEnd();
          } while( true );
        }
      }
      *ppuVar6 = puVar36;
      if (1 < (int)(uVar15 + 1)) {
        local_1c4 = (float ****)uVar15;
        if ((uVar15 & 3) != 0) {
          do {
            loopEnd();
          } while( true );
        }
        if (uVar15 >> 2 != 0) {
          do {
            loopEnd();
          } while( true );
        }
      }
      fVar37 = -(float)ppppfVar5[1] / fVar35;
      pppfVar31 = (float ***)((1.0 - fVar37 * fVar37) * fVar35);
      if (1 < (int)(uVar15 + 1)) {
        local_1c4 = (float ****)uVar15;
        pfVar24 = pfVar8 + 10;
        ppuVar25 = local_158;
        if ((uVar15 & 3) != 0) {
          do {
            *pfVar24 = (float)*ppuVar25 + fVar37 * (float)*ppuVar6;
            ppuVar25 = ppuVar25 + 1;
            pfVar24 = pfVar24 + 1;
            ppuVar6 = ppuVar6 + -1;
            loopEnd();
          } while( true );
        }
        if (uVar15 >> 2 != 0) {
          do {
            *pfVar24 = (float)*ppuVar25 + fVar37 * (float)*ppuVar6;
            pfVar24[1] = (float)ppuVar25[1] + fVar37 * (float)ppuVar6[-1];
            pfVar24[2] = (float)ppuVar25[2] + fVar37 * (float)ppuVar6[-2];
            pfVar24[3] = (float)ppuVar25[3] + fVar37 * (float)ppuVar6[-3];
            ppuVar25 = ppuVar25 + 4;
            pfVar24 = pfVar24 + 4;
            ppuVar6 = ppuVar6 + -4;
            loopEnd();
          } while( true );
        }
      }
      pfVar9[2] = fVar37;
      uVar16 = uVar15 + 2;
      ppuVar6 = ppuVar6 + 2;
      pfVar9 = pfVar9 + 2;
      ppppfVar5 = ppppfVar5 + 2;
      if ((int)ppppfVar13 < (int)uVar16) break;
      fVar35 = -(float)*ppppfVar5;
      if (1 < (int)uVar16) {
        local_1c4 = (float ****)(uVar15 + 1);
        if (((uint)local_1c4 & 3) != 0) {
          do {
            loopEnd();
          } while( true );
        }
        if ((uint)local_1c4 >> 2 != 0) {
          do {
            loopEnd();
          } while( true );
        }
      }
    }
    *pfVar4 = (float)pppfVar34 / (float)pppfVar31;
    ppppfVar29 = ppppfVar29 + 9;
    pfVar4 = pfVar4 + 1;
    local_1b4 = (float *)((int)local_1b4 + -1);
    pfVar8 = pfVar11;
  } while (local_1b4 != (float *)0x0);
  piVar14 = param_5 + 2;
  piVar23 = param_5 + 4;
  pfVar8 = local_1a8 + 2;
  local_1c0 = (float ******)((int)ppppfVar13 + -1);
  local_1c4 = ppppfVar13;
  iVar3 = 0;
  pfVar4 = afStack_13c + 1;
  local_158[0] = (undefined1 *)((int)ppppfVar13 + -2);
  local_1ac = local_1bc;
  local_1b0 = afStack_13c + (int)ppppfVar13;
  local_1b4 = local_1a8 + (int)((int)ppppfVar13 + 1);
  do {
    *piVar14 = 0;
    if ((param_3 == '\0') &&
       (ppppfVar29 = *local_1ac, -1 < (int)((uint)((float)ppppfVar29 < fVar32) << 0x1f))) {
      if (((char)param_5[1] != '\0') && ((int)((uint)((float)ppppfVar29 < 2.0) << 0x1f) < 0)) {
        fVar30 = 1.0 - (2.0 - (float)ppppfVar29) * fVar30 * 2.0;
        *pfVar8 = *pfVar8 * fVar30;
        fVar32 = fVar30 * fVar30 * fVar30;
        pfVar8[1] = pfVar8[1] * fVar30 * fVar30;
        pfVar8[2] = pfVar8[2] * fVar32;
        fVar32 = fVar32 * fVar30;
        fVar35 = fVar32 * fVar30;
        pfVar8[3] = pfVar8[3] * fVar32;
        pfVar8[4] = pfVar8[4] * fVar35;
        fVar35 = fVar35 * fVar30;
        fVar32 = fVar35 * fVar30;
        pfVar8[5] = pfVar8[5] * fVar35;
        pfVar8[6] = pfVar8[6] * fVar32;
        pfVar8[7] = fVar32 * fVar30 * pfVar8[7];
      }
      fVar30 = *local_1b4;
      if (0 < (int)local_1c0) {
        do {
          local_15c = local_1c0;
          local_dc[0] = (float ***)
                        ((*pfVar8 - fVar30 * local_1a8[(int)(iVar3 * 9 + (int)ppppfVar13)]) /
                        (1.0 - fVar30 * fVar30));
          local_1c0 = &local_1ac + (int)(iVar3 * 9 + (int)ppppfVar13);
          loopEnd();
        } while( true );
      }
      *local_1b0 = fVar30;
      ppppfVar29 = local_dc;
      if (0 < (int)local_158[0]) {
        pfVar8 = pfVar4 + (int)local_158[0];
        ppppfVar5 = local_dc;
        do {
          ppppfVar26 = ppppfVar5 + (int)local_158[0];
          pppfVar31 = *ppppfVar26;
          ppppfVar29 = local_f8 + ((uint)local_158[0] & 1) * 7;
          *pfVar8 = (float)pppfVar31;
          fVar30 = 1.0 - (float)pppfVar31 * (float)pppfVar31;
          ppppfVar12 = (float ****)0x0;
          local_15c = (float ******)local_158[0];
          if (((uint)local_158[0] & 3) != 0) {
            do {
              ppppfVar26 = ppppfVar26 + -1;
              *ppppfVar29 = (float ***)(((float)*ppppfVar5 - *pfVar8 * (float)*ppppfVar26) / fVar30)
              ;
              ppppfVar5 = ppppfVar5 + 1;
              ppppfVar29 = ppppfVar29 + 1;
              loopEnd();
              pfVar8 = (float *)((uint)pfVar8 >> 8);
            } while( true );
          }
          puVar36 = local_158[0] + -1;
          if ((uint)local_158[0] >> 2 != 0) {
            do {
              ppppfVar13 = ppppfVar5 + ((int)puVar36 - (int)ppppfVar12);
              ppppfVar26 = ppppfVar29 + (int)ppppfVar12;
              ppppfVar12 = ppppfVar5 + (int)ppppfVar12;
              *ppppfVar26 = (float ***)
                            (((float)*ppppfVar12 - *pfVar8 * (float)*ppppfVar13) / fVar30);
              ppppfVar26[1] =
                   (float ***)(((float)ppppfVar12[1] - *pfVar8 * (float)ppppfVar13[-1]) / fVar30);
              ppppfVar26[2] =
                   (float ***)(((float)ppppfVar12[2] - *pfVar8 * (float)ppppfVar13[-2]) / fVar30);
              ppppfVar26[3] =
                   (float ***)(((float)ppppfVar12[3] - *pfVar8 * (float)ppppfVar13[-3]) / fVar30);
              ppppfVar12 = ppppfVar12 + 4;
              loopEnd();
              pfVar8 = (float *)((uint)pfVar8 >> 8);
            } while( true );
          }
          pfVar8 = pfVar8 + -1;
          ppppfVar5 = ppppfVar29;
          local_158[0] = puVar36;
        } while (0 < (int)puVar36);
      }
      do {
        iVar3 = DAT_0059b688;
        *pfVar4 = (float)*ppppfVar29;
        *piVar14 = (int)ppppfVar13;
        fVar30 = ABS(*pfVar4);
        if (fVar33 <= fVar30) {
          iVar22 = 4;
        }
        else {
          iVar22 = 0;
        }
        iVar18 = iVar22;
        if ((((-1 < (int)((uint)(fVar30 < *(float *)(iVar3 + iVar22 * 4)) << 0x1f)) &&
             (iVar18 = iVar22 + 1,
             -1 < (int)((uint)(fVar30 < *(float *)(iVar3 + iVar18 * 4)) << 0x1f))) &&
            (iVar18 = iVar22 + 2,
            -1 < (int)((uint)(fVar30 < *(float *)(iVar3 + iVar18 * 4)) << 0x1f))) &&
           (iVar18 = iVar22 + 3, -1 < (int)((uint)(fVar30 < *(float *)(iVar3 + iVar18 * 4)) << 0x1f)
           )) {
          iVar18 = iVar22 + 4;
        }
        if (*pfVar4 < 0.0) {
          iVar18 = -iVar18;
        }
        ppppfVar29 = local_1c4;
        if (iVar18 == 0) {
          *piVar23 = 0;
          ppppfVar29 = (float ****)(*piVar14 + -1);
        }
        *piVar23 = iVar18;
        *piVar14 = (int)ppppfVar29;
        loopEnd();
        ppppfVar29 = local_1c4;
      } while( true );
    }
    iVar3 = iVar3 + 1;
    pfVar8 = pfVar8 + 9;
    local_1b4 = local_1b4 + 9;
    pfVar4 = pfVar4 + 8;
    local_1b0 = local_1b0 + 8;
    piVar23 = piVar23 + 8;
    local_1ac = local_1ac + 1;
    piVar14 = piVar14 + 1;
  } while (iVar3 < *param_5);
  if ((local_2c == '\0') || ((int)local_1c8 < 3)) {
    iVar3 = 1;
  }
  else {
    iVar3 = 2;
  }
  if ((int)local_1c8 < 4) {
    iVar22 = (int)local_1c8 << 2;
  }
  else {
    iVar22 = 0x10;
  }
  iVar18 = *(int *)(DAT_0059b68c + iVar22);
  local_1c8 = 0.0;
  local_1c4 = (float ****)0x0;
  local_1c0 = (float ******)0x0;
  local_1bc[0] = (float ****)0x0;
  local_1bc[1] = (float ****)0x0;
  local_1b4 = (float *)0x0;
  local_1b0 = (float *)0x0;
  local_1ac = (float *****)0x0;
  iVar27 = 0;
  param_5 = param_5 + 2;
  pfVar8 = afStack_13c + 1;
  iVar22 = (int)local_1a8[0] * 3;
  do {
    iVar7 = *param_5;
    iVar27 = iVar27 + 1;
    iVar17 = iVar27 * (iVar18 * (int)local_1a8[0] >> (iVar3 + 0xffU & 0xff));
    if ((iVar7 != 0) && (iVar22 < iVar17)) {
      pfVar4 = (float *)(param_6 + iVar22 * 4);
      iVar22 = iVar17 - iVar22;
      do {
        fVar30 = *pfVar4;
        iVar19 = 0;
        fVar33 = fVar30;
        if (0 < iVar7) {
          do {
            fVar32 = (&local_1c8)[iVar19];
            (&local_1c8)[iVar19] = fVar33;
            fVar33 = pfVar8[iVar19] * fVar30;
            iVar20 = iVar19 + 1;
            fVar30 = fVar30 + pfVar8[iVar19] * fVar32;
            if (iVar7 <= iVar20) break;
            fVar35 = (&local_1c8)[iVar20];
            (&local_1c8)[iVar20] = fVar32 + fVar33;
            fVar33 = pfVar8[iVar20] * fVar30;
            iVar21 = iVar19 + 2;
            fVar30 = fVar30 + pfVar8[iVar20] * fVar35;
            if (iVar7 <= iVar21) break;
            fVar32 = (&local_1c8)[iVar21];
            (&local_1c8)[iVar21] = fVar35 + fVar33;
            fVar33 = pfVar8[iVar21] * fVar30;
            iVar20 = iVar19 + 3;
            fVar30 = fVar30 + pfVar8[iVar21] * fVar32;
            if (iVar7 <= iVar20) break;
            fVar35 = (&local_1c8)[iVar20];
            (&local_1c8)[iVar20] = fVar32 + fVar33;
            fVar33 = fVar35 + pfVar8[iVar20] * fVar30;
            iVar19 = iVar19 + 4;
            fVar30 = fVar30 + pfVar8[iVar20] * fVar35;
          } while (iVar19 < iVar7);
        }
        *pfVar4 = fVar30;
        pfVar4 = pfVar4 + 1;
        iVar22 = iVar22 + -1;
      } while (iVar22 != 0);
    }
    pfVar8 = pfVar8 + 8;
    param_5 = param_5 + 1;
    iVar22 = iVar17;
    if (iVar3 <= iVar27) {
      return;
    }
  } while( true );
}

