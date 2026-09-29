
/* WARNING: Instruction at (ram,0x0059bc2e) overlaps instruction at (ram,0x0059bc2c)
    */

void FUN_0059bae4(byte param_1,byte param_2,int param_3,undefined4 param_4,undefined4 param_5,
                 float *param_6,float *param_7,int *param_8)

{
  longlong lVar1;
  bool bVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  int *piVar8;
  int *piVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  uint uVar13;
  uint uVar14;
  int iVar15;
  int iVar16;
  float *pfVar17;
  int iVar18;
  int iVar19;
  float *pfVar20;
  int iVar21;
  int iVar22;
  int *piVar23;
  uint in_fpscr;
  float fVar24;
  undefined4 uVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float local_408 [240];
  
  iVar3 = FUN_0059ba96();
  fVar26 = DAT_0059bc08;
  uVar14 = (uint)param_2;
  lVar1 = (longlong)(param_3 + -1) * (longlong)DAT_0059c78c;
  iVar10 = (int)((ulonglong)lVar1 >> 0x20);
  iVar19 = (iVar10 >> 6) - (iVar10 >> 0x1f);
  if (1 < iVar19) {
    iVar19 = 2;
  }
  iVar10 = FUN_00599050(param_2,iVar10,(int)lVar1);
  iVar4 = FUN_004396b8(param_4);
  iVar5 = FUN_0059b4b8(param_5);
  iVar5 = ((((((param_3 * 8 - iVar3) - (uint)(4 < uVar14)) - iVar19) - iVar10) - iVar4) - iVar5) +
          -0x34;
  fVar27 = *param_6;
  fVar24 = (float)VectorSignedToFloat(param_6[1],(byte)(in_fpscr >> 0x16) & 3);
  uVar25 = FUN_00439f88(fVar24 + fVar27,DAT_0059bebc);
  fVar24 = (float)FUN_00439efc(uVar25,DAT_0059bec0);
  fVar24 = fVar27 * DAT_0059bec4 + fVar24 * DAT_0059bec8;
  iVar19 = FUN_0059b6d0(param_2,param_3);
  uVar6 = (uint)param_1;
  iVar10 = 0;
  iVar4 = uVar6 + 1;
  iVar3 = iVar4 * *(int *)(DAT_0059c178 + uVar14 * 4);
  iVar3 = (int)(iVar3 + ((uint)(iVar3 >> 1) >> 0x1e)) >> 2;
  if (4 < uVar14) {
    iVar18 = (int)(&DAT_0059c170)[uVar14 + uVar6 * 2] + (param_3 << 5) / ((short)iVar4 * 0x7d);
    if (iVar18 < 7) {
      iVar10 = -0x3000000;
    }
    else {
      iVar10 = DAT_0059c790;
      if (iVar18 < 0x17) {
        iVar10 = iVar18 * -0x800000;
      }
    }
    if (0 < iVar3) {
      do {
        loopEnd();
      } while( true );
    }
    fVar26 = (float)VectorSignedToFloat(iVar4,(byte)(in_fpscr >> 0x16) & 3);
    fVar27 = (float)FUN_00577d08((DAT_0059becc * DAT_0059bed4) / (fVar26 * DAT_0059becc));
    fVar26 = DAT_0059bed0;
    if ((int)fVar27 < 8) {
      fVar26 = (float)(8 - (int)fVar27);
    }
    fVar26 = (float)VectorSignedToFloat(fVar26,(byte)(in_fpscr >> 0x16) & 3);
    fVar26 = -fVar26;
  }
  if (0 < iVar3) {
    pfVar20 = local_408;
    iVar4 = iVar3;
    pfVar17 = param_7;
    fVar27 = DAT_0059bed0;
    do {
      fVar28 = *pfVar17 * *pfVar17;
      fVar29 = pfVar17[1] * pfVar17[1];
      fVar30 = pfVar17[2] * pfVar17[2];
      fVar31 = pfVar17[3] * pfVar17[3];
      uVar25 = FUN_00439f88(fVar27,fVar28);
      uVar25 = FUN_00439f88(uVar25,fVar29);
      uVar25 = FUN_00439f88(uVar25,fVar30);
      fVar27 = (float)FUN_00439f88(uVar25,fVar31);
      *pfVar20 = fVar28 + fVar29 + fVar30 + fVar31;
      pfVar17 = pfVar17 + 4;
      pfVar20 = pfVar20 + 1;
      iVar4 = iVar4 + -1;
    } while (iVar4 != 0);
  }
  fVar28 = (float)FUN_004397a8();
  iVar4 = DAT_0059c174;
  uVar25 = DAT_0059bef0;
  fVar27 = DAT_0059bed0;
  if (4 < uVar14) {
    fVar27 = fVar28;
    if (((uint)fVar28 & 0x7f800000) != 0) {
      fVar27 = (float)(iVar10 + (int)fVar28);
    }
    fVar29 = fVar26 + DAT_0059bed8;
    fVar26 = fVar26 - (fVar29 + DAT_0059bedc);
    fVar27 = fVar27 * (float)((int)(((DAT_0059beec +
                                     (DAT_0059bee8 + (DAT_0059bee4 + fVar26 * DAT_0059bee0) * fVar26
                                     ) * fVar26) * fVar26 + 1.0) *
                                   *(float *)(&DAT_0059c1a4 + ((uint)fVar29 & 7) * 4)) +
                             ((int)fVar29 >> 3) * 0x800000);
  }
  if (0 < iVar3) {
    iVar10 = iVar3;
    pfVar17 = local_408;
    do {
      fVar26 = (float)FUN_00439f88(*pfVar17 + fVar27,uVar25);
      fVar26 = fVar26 * fVar26;
      iVar18 = iVar4 + (((uint)fVar26 & 0x7fffff) >> 0x12) * 4;
      iVar10 = iVar10 + -1;
      *pfVar17 = (float)((((uint)fVar26 >> 0x16) - 0xfe) * 0xc0a9 + (uint)*(ushort *)(iVar18 + 0x54)
                        + ((int)((((uint)fVar26 & 0x3ffff) >> 2) * (uint)*(ushort *)(iVar18 + 0x56))
                          >> 0x10));
      pfVar17 = pfVar17 + 1;
    } while (iVar10 != 0);
  }
  iVar10 = DAT_0059c174;
  fVar26 = (float)VectorSignedToFloat(iVar5,(byte)(in_fpscr >> 0x16) & 3);
  iVar18 = 0xff - iVar19;
  iVar7 = 0x80;
  iVar3 = iVar3 + -1;
  iVar4 = iVar18;
  do {
    iVar11 = iVar4 - iVar7;
    iVar12 = 0;
    iVar15 = iVar3;
    if (-1 < iVar3) {
      pfVar17 = local_408 + iVar3;
      do {
        if (iVar11 * 0xb6db <= (int)*pfVar17) break;
        iVar15 = iVar15 + -1;
        pfVar17 = pfVar17 + -1;
      } while (-1 < iVar15);
    }
    if (-1 < iVar15) {
      pfVar17 = local_408 + iVar15;
      iVar16 = iVar15;
      do {
        iVar21 = (int)*pfVar17 + iVar11 * -0xb6db;
        iVar22 = DAT_0059c798;
        if (-1 < iVar21) {
          if (iVar21 < 0x2b0000) {
            iVar22 = iVar21 + 0x70000;
          }
          else {
            iVar22 = iVar21 * 2 + -0x240000;
          }
        }
        iVar12 = iVar12 + iVar22;
        iVar16 = iVar16 + -1;
        pfVar17 = pfVar17 + -1;
      } while (-1 < iVar16);
    }
    if (iVar12 <= DAT_0059c794 * (int)(fVar26 + fVar24 + 0.5)) {
      iVar4 = iVar11;
      iVar15 = iVar3;
    }
    iVar3 = iVar15;
    iVar7 = iVar7 >> 1;
  } while (iVar7 != 0);
  fVar26 = DAT_0059c168;
  if (4 < uVar14) {
    fVar26 = DAT_0059c16c;
  }
  iVar3 = 0x80;
  do {
    fVar27 = 1.0;
    piVar8 = (int *)(iVar18 - iVar3);
    for (piVar23 = piVar8; (int)piVar23 < 0; piVar23 = piVar23 + 7) {
      fVar27 = fVar27 * DAT_0059c170;
    }
    piVar9 = piVar8;
    if (0x1b < (int)piVar23) {
      iVar3 = (int)((ulonglong)((longlong)(int)piVar23 * (longlong)DAT_0059c79c) >> 0x20) +
              (int)piVar23;
      uVar13 = (iVar3 >> 4) - (iVar3 >> 0x1f);
      if ((uVar13 & 3) != 0) {
        do {
          loopEnd();
        } while( true );
      }
      piVar9 = (int *)*piVar8;
      iVar3 = piVar8[1];
      if (uVar13 >> 2 != 0) {
        do {
          loopEnd();
        } while( true );
      }
    }
    if ((int)((uint)(fVar28 < fVar27 * *(float *)(DAT_0059c174 + (int)piVar23 * 4 + 0xd4) * fVar26)
             << 0x1f) < 0) {
      iVar18 = (int)piVar9;
    }
    iVar3 = iVar3 >> 1;
  } while (0 < iVar3);
  if ((iVar4 < iVar18) || (fVar28 == 0.0)) {
    bVar2 = true;
    iVar4 = iVar18;
  }
  else {
    bVar2 = false;
  }
  FUN_0059b76c(fVar26,0x41200000,param_1,param_2,iVar4,param_7,param_8 + 1);
  iVar3 = FUN_0059b852(param_1,param_2,param_3,param_7,param_8 + 1,0,0);
  if (bVar2) {
    *param_6 = 0.0;
    fVar26 = 0.0;
  }
  else {
    *param_6 = fVar24;
    fVar26 = (float)(iVar5 - iVar3);
  }
  iVar15 = 0x30;
  param_6[1] = fVar26;
  piVar23 = (int *)(iVar10 + uVar14 * 0xc);
  iVar7 = iVar4 + iVar19;
  if (iVar3 < *piVar23) {
    iVar10 = (iVar3 + 0x30) * 3;
  }
  else {
    iVar10 = *(int *)(iVar10 + 4 + uVar14 * 0xc);
    if (iVar3 < iVar10) {
      iVar11 = iVar10 - *piVar23;
      iVar15 = iVar11 * 0x30;
      iVar10 = iVar11 * (*piVar23 + 0x30) * 3 +
               (iVar10 + (*piVar23 + 0x30) * -3) * (iVar3 - *piVar23);
    }
    else {
      iVar10 = piVar23[2];
      if (iVar3 < piVar23[2]) {
        iVar10 = iVar3;
      }
    }
  }
  iVar15 = (iVar10 + iVar15 / 2) / iVar15;
  if (uVar14 < 5) {
    if (iVar3 < (iVar5 - iVar15) + -2) {
      iVar10 = -(uint)(iVar18 + iVar19 < iVar7);
    }
    else {
      if (iVar3 <= iVar5) goto LAB_0059c162;
      if (iVar7 < 0xff) {
        iVar10 = 1;
        if ((iVar7 < 0xfe) && (iVar15 + iVar5 <= iVar3)) {
          iVar10 = 2;
        }
      }
      else {
        iVar10 = 0;
      }
    }
  }
  else {
    if (iVar3 <= iVar5) {
LAB_0059c162:
      iVar10 = 0;
      goto LAB_0059c0f0;
    }
    if (iVar3 < 0x208) {
      iVar10 = 1;
    }
    else {
      iVar10 = 2;
    }
    iVar10 = iVar10 * -((int)-(uint)(param_1 == 0) >> 0x1f) + (uint)(uVar6 < 2) + 1;
    iVar10 = (iVar10 * (iVar3 - iVar5)) / iVar15 + iVar10 + iVar7;
    if (0xff < iVar10) {
      iVar10 = 0xff;
    }
    iVar10 = iVar10 - iVar7;
  }
  if (iVar10 != 0) {
    FUN_0059b76c(param_1,param_2,iVar10,param_7,param_8 + 1);
  }
LAB_0059c0f0:
  *param_8 = iVar19 + iVar10 + iVar4;
  FUN_0059b852(param_1,param_2,param_3,param_7,param_8 + 1,iVar5,param_8 + 2);
  return;
}

