
int FUN_005653a0(float param_1,float param_2,float param_3,float param_4,undefined4 param_5,
                undefined4 param_6,float param_7,float param_8)

{
  float fVar1;
  float fVar2;
  int *piVar3;
  byte bVar4;
  uint uVar5;
  int iVar6;
  bool bVar7;
  int iVar8;
  uint *puVar9;
  uint uVar10;
  int iVar11;
  int iVar12;
  bool bVar13;
  float fVar14;
  float fVar15;
  float extraout_s3;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  undefined8 uVar21;
  
  piVar3 = DAT_005657d4;
  fVar2 = DAT_005653b8;
  fVar1 = DAT_005653b4;
  iVar11 = 1;
  uVar21 = CONCAT44(param_6,param_5);
  fVar20 = param_4;
  do {
    puVar9 = (uint *)*piVar3;
    bVar7 = false;
    fVar14 = (float)puVar9[0xd];
    bVar13 = NAN(fVar14) || NAN(param_1);
    if (fVar14 >= param_1) {
      bVar13 = NAN(fVar14) || NAN(param_2);
    }
    fVar16 = (float)uVar21;
    fVar17 = (float)((ulonglong)uVar21 >> 0x20);
    if ((fVar14 < param_1 || fVar14 < param_2) == bVar13) {
      fVar15 = (float)puVar9[0xc];
      bVar13 = NAN(param_1) || NAN(fVar15);
      if (param_1 >= fVar15) {
        bVar13 = NAN(param_2) || NAN(fVar15);
      }
      if ((param_1 < fVar15 || param_2 < fVar15) == bVar13) {
        bVar13 = NAN(fVar14) || NAN(param_3);
        if (fVar14 >= param_3) {
          bVar13 = NAN(fVar14) || NAN(fVar20);
        }
        if ((fVar14 < param_3 || fVar14 < fVar20) == bVar13) {
          bVar13 = NAN(param_3) || NAN(fVar15);
          if (param_3 >= fVar15) {
            bVar13 = NAN(fVar20) || NAN(fVar15);
          }
          if ((param_3 < fVar15 || fVar20 < fVar15) == bVar13) {
            bVar13 = NAN(fVar14) || NAN(fVar16);
            if (fVar14 >= fVar16) {
              bVar13 = NAN(fVar14) || NAN(fVar17);
            }
            if ((fVar14 < fVar16 || fVar14 < fVar17) == bVar13) {
              bVar13 = NAN(fVar16) || NAN(fVar15);
              if (fVar16 >= fVar15) {
                bVar13 = NAN(fVar17) || NAN(fVar15);
              }
              if ((fVar16 < fVar15 || fVar17 < fVar15) == bVar13) {
                bVar13 = NAN(fVar14) || NAN(param_7);
                if (fVar14 >= param_7) {
                  bVar13 = NAN(fVar14) || NAN(param_8);
                  param_4 = param_8;
                }
                if ((fVar14 < param_7 || fVar14 < param_8) == bVar13) {
                  bVar13 = NAN(param_7) || NAN(fVar15);
                  if (param_7 >= fVar15) {
                    bVar13 = NAN(param_4) || NAN(fVar15);
                  }
                  if ((param_7 < fVar15 || param_4 < fVar15) == bVar13) {
                    bVar7 = true;
                  }
                }
              }
            }
          }
        }
      }
    }
    fVar15 = (float)puVar9[0xc] + fVar2;
    bVar13 = NAN(param_1) || NAN(fVar15);
    fVar14 = fVar14 + fVar1;
    if (param_1 < fVar15) {
      bVar13 = NAN(param_3) || NAN(fVar15);
    }
    if ((param_1 < fVar15 && param_3 < fVar15) == bVar13) {
LAB_005654dc:
      bVar13 = NAN(fVar14) || NAN(param_1);
      if (fVar14 < param_1) {
        bVar13 = NAN(fVar14) || NAN(param_3);
      }
      if ((fVar14 < param_1 && fVar14 < param_3) != bVar13) {
        bVar13 = NAN(fVar14) || NAN(fVar16);
        if (fVar14 < fVar16) {
          bVar13 = NAN(fVar14) || NAN(param_7);
        }
        if ((fVar14 < fVar16 && fVar14 < param_7) != bVar13) goto LAB_00565554;
      }
      bVar13 = NAN(param_2) || NAN(fVar15);
      if (param_2 < fVar15) {
        bVar13 = NAN(fVar20) || NAN(fVar15);
      }
      if ((param_2 < fVar15 && fVar20 < fVar15) != bVar13) {
        bVar13 = NAN(fVar17) || NAN(fVar15);
        if (fVar17 < fVar15) {
          bVar13 = NAN(param_8) || NAN(fVar15);
        }
        if ((fVar17 < fVar15 && param_8 < fVar15) != bVar13) goto LAB_00565554;
      }
      if ((fVar14 < param_2 && (fVar14 < param_2 && fVar14 < fVar20)) &&
         (fVar14 < fVar17 && (fVar14 < fVar17 && fVar14 < param_8))) goto LAB_00565554;
      bVar4 = 0;
    }
    else {
      bVar13 = NAN(fVar16) || NAN(fVar15);
      if (fVar16 < fVar15) {
        bVar13 = NAN(param_7) || NAN(fVar15);
      }
      if ((fVar16 < fVar15 && param_7 < fVar15) == bVar13) goto LAB_005654dc;
LAB_00565554:
      bVar4 = 1;
    }
    if (bVar7) {
      if ((bool)(bVar4 ^ 1)) {
LAB_0056556a:
        uVar5 = puVar9[3];
        if (puVar9[0xb] == 0) {
          if (uVar5 < *puVar9) {
            *(undefined1 *)(puVar9[7] + uVar5) = 6;
            *(int *)(*piVar3 + 0xc) = *(int *)(*piVar3 + 0xc) + 1;
          }
          else {
            puVar9[10] = 2;
            puVar9[3] = puVar9[3] + 1;
            puVar9[0xb] = 1;
          }
        }
        else {
          puVar9[3] = uVar5 + 1;
        }
        iVar8 = *piVar3;
        iVar6 = *(int *)(iVar8 + 8);
        if (*(int *)(iVar8 + 0x2c) == 0) {
          uVar10 = *(uint *)(iVar8 + 4);
          uVar5 = iVar6 + 1;
          if (uVar5 < uVar10) {
            iVar12 = *(int *)(iVar8 + 0x10);
            *(float *)(iVar12 + iVar6 * 4) = param_3;
            *(uint *)(iVar8 + 8) = uVar5;
            *(float *)(iVar12 + uVar5 * 4) = fVar20;
            uVar5 = iVar6 + 3;
            *(int *)(iVar8 + 8) = iVar6 + 2;
            if (uVar5 < uVar10) {
              *(float *)(iVar12 + (iVar6 + 2) * 4) = fVar16;
              *(uint *)(iVar8 + 8) = uVar5;
              *(float *)(iVar12 + uVar5 * 4) = fVar17;
              uVar5 = iVar6 + 5;
              *(int *)(iVar8 + 8) = iVar6 + 4;
              if (uVar5 < uVar10) {
                *(float *)(iVar12 + (iVar6 + 4) * 4) = param_7;
                *(uint *)(iVar8 + 8) = uVar5;
                *(float *)(iVar12 + uVar5 * 4) = param_8;
                *(int *)(iVar8 + 8) = iVar6 + 6;
                param_4 = param_8;
              }
              else {
                *(int *)(iVar8 + 8) = iVar6 + 6;
                *(undefined4 *)(iVar8 + 0x28) = 2;
                *(undefined4 *)(iVar8 + 0x2c) = 1;
                param_4 = param_8;
              }
            }
            else {
              *(undefined4 *)(iVar8 + 0x28) = 2;
              *(int *)(iVar8 + 8) = iVar6 + 4;
              *(undefined4 *)(iVar8 + 0x2c) = 1;
              *(int *)(iVar8 + 8) = *(int *)(iVar8 + 8) + 2;
              param_4 = param_8;
            }
            goto LAB_005655c8;
          }
          *(int *)(iVar8 + 8) = iVar6 + 2;
          *(undefined4 *)(iVar8 + 0x28) = 2;
          *(undefined4 *)(iVar8 + 0x2c) = 1;
        }
        else {
          *(int *)(iVar8 + 8) = iVar6 + 2;
        }
        *(int *)(iVar8 + 8) = *(int *)(iVar8 + 8) + 2;
        *(int *)(iVar8 + 8) = *(int *)(iVar8 + 8) + 2;
        param_4 = param_8;
      }
      else {
LAB_005655b8:
        iVar6 = FUN_00564974(param_1,param_2);
        param_4 = extraout_s3;
        if (iVar6 != 0) {
          FUN_0051778c(0);
          FUN_00517796(0);
          FUN_0051565c(iVar6);
          return iVar6;
        }
      }
LAB_005655c8:
      iVar11 = iVar11 + -1;
      iVar6 = *piVar3;
      if (*(int *)(iVar6 + 700) != 0) {
        iVar8 = *(int *)(iVar6 + 700) + -1;
        *(int *)(iVar6 + 700) = iVar8;
        iVar6 = iVar6 + iVar8 * 0x18;
        param_3 = *(float *)(iVar6 + 0x1cc);
        fVar20 = *(float *)(iVar6 + 0x1d0);
        uVar21 = *(undefined8 *)(iVar6 + 0x1d4);
        param_1 = param_7;
        param_2 = param_8;
        param_7 = *(float *)(iVar6 + 0x1dc);
        param_8 = *(float *)(iVar6 + 0x1e0);
      }
    }
    else {
      if (!(bool)(bVar4 ^ 1)) goto LAB_005655b8;
      if (9 < (int)puVar9[0xaf]) goto LAB_0056556a;
      fVar14 = (param_3 + fVar16) * 0.5;
      fVar15 = (fVar20 + fVar17) * 0.5;
      fVar16 = (fVar16 + param_7) * 0.5;
      fVar17 = (fVar17 + param_8) * 0.5;
      fVar18 = (fVar14 + fVar16) * 0.5;
      puVar9[puVar9[0xaf] * 6 + 0x73] = (uint)fVar18;
      fVar19 = (fVar15 + fVar17) * 0.5;
      puVar9[puVar9[0xaf] * 6 + 0x74] = (uint)fVar19;
      fVar20 = (param_2 + fVar20) * 0.5;
      puVar9[puVar9[0xaf] * 6 + 0x75] = (uint)fVar16;
      puVar9[puVar9[0xaf] * 6 + 0x76] = (uint)fVar17;
      param_3 = (param_1 + param_3) * 0.5;
      puVar9[puVar9[0xaf] * 6 + 0x77] = (uint)param_7;
      param_4 = (param_3 + fVar14) * 0.5;
      fVar14 = (fVar20 + fVar15) * 0.5;
      uVar21 = CONCAT44(fVar14,param_4);
      puVar9[puVar9[0xaf] * 6 + 0x78] = (uint)param_8;
      param_4 = param_4 + fVar18;
      param_7 = param_4 * 0.5;
      param_8 = (fVar14 + fVar19) * 0.5;
      puVar9[0xaf] = puVar9[0xaf] + 1;
      iVar11 = iVar11 + 1;
    }
    if (iVar11 == 0) {
      return 0;
    }
  } while( true );
}

