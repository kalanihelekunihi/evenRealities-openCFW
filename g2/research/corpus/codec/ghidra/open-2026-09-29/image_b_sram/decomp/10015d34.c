
/* WARNING: Control flow encountered bad instruction data */

void FUN_10015d34(float *param_1,undefined4 param_2,int param_3)

{
  short *psVar1;
  short sVar2;
  int iVar3;
  float *pfVar4;
  float *pfVar5;
  undefined4 *puVar6;
  undefined2 *puVar7;
  float fVar8;
  undefined4 *puVar9;
  uint *puVar10;
  int iVar11;
  float *pfVar12;
  uint uVar13;
  short *psVar14;
  float *pfVar15;
  float *pfVar16;
  short *psVar17;
  float *pfVar18;
  undefined4 *puVar19;
  float fVar20;
  uint *puVar21;
  float fVar22;
  uint uVar23;
  float *pfVar24;
  uint *puVar25;
  undefined4 *puVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  undefined4 uVar30;
  undefined2 *puVar31;
  float fVar32;
  int iVar33;
  float fVar34;
  int iVar35;
  float fVar36;
  float fVar37;
  float fVar38;
  short local_24;
  
  FUN_10009968(param_1[9],(int)param_1[5] * 2 + (int)param_1[9],
               ((int)param_1[3] - (int)param_1[5]) * 2);
  FUN_10009968(((int)param_1[3] - (int)param_1[5]) * 2 + (int)param_1[9],param_2,
               (int)param_1[5] << 1);
  fVar27 = param_1[3];
  puVar31 = (undefined2 *)param_1[0xe];
  if (0 < (int)fVar27) {
    puVar10 = (uint *)param_1[9];
    puVar21 = (uint *)param_1[0xc];
    puVar25 = (uint *)((int)puVar10 + (int)fVar27 * 2);
    puVar7 = puVar31;
    do {
      uVar13 = *puVar10;
      puVar10 = (uint *)((int)puVar10 + 2);
      uVar23 = *puVar21;
      puVar21 = (uint *)((int)puVar21 + 2);
      *puVar7 = (short)((int)((uVar23 & 0xffff) * (uVar13 & 0xffff)) >> 0xf);
      puVar7 = puVar7 + 1;
    } while (puVar25 != puVar10);
  }
  FUN_100113c4(puVar31 + (int)fVar27,0,((int)param_1[4] - (int)fVar27) * 2);
  fVar27 = param_1[0xe];
  fVar20 = param_1[6];
  iVar3 = FUN_1000e2c4(fVar27,fVar20);
  iVar3 = (uint)(iVar3 < -9) * -9 + (uint)(iVar3 >= -9) * iVar3;
  FUN_1000e28c(fVar27,fVar20,iVar3);
  gx8002_backup_rfft(DAT_100161c0,param_1[0xe],param_1[0xf]);
  fVar27 = param_1[7];
  fVar20 = (float)(1 << (iVar3 + 9U & 0x3f));
  if ((int)fVar27 < 1) {
    fVar20 = param_1[8];
    if (fVar20 == 0.0) {
      iVar11 = (int)fVar27 << 2;
      goto LAB_10016648;
    }
  }
  else {
    pfVar4 = (float *)param_1[0x10];
    psVar14 = (short *)param_1[0xf];
    iVar11 = (int)fVar27 * 4;
    psVar17 = psVar14 + (int)fVar27 * 2;
    pfVar12 = pfVar4;
    do {
      sVar2 = *psVar14;
      psVar1 = psVar14 + 1;
      psVar14 = psVar14 + 2;
      *pfVar12 = (float)(int)sVar2 * (float)(int)sVar2 * fVar20 +
                 (float)(int)*psVar1 * (float)(int)*psVar1 * fVar20;
      pfVar12 = pfVar12 + 1;
    } while (psVar17 != psVar14);
    fVar20 = param_1[8];
    if (fVar20 == 0.0) {
LAB_10016648:
      fVar20 = param_1[0x1d];
      puVar9 = (undefined4 *)param_1[0x1e];
      if (0 < (int)fVar20) {
        puVar6 = (undefined4 *)param_1[0x10];
        puVar26 = puVar6 + (int)fVar20;
        puVar19 = puVar9;
        do {
          uVar30 = *puVar6;
          puVar6 = puVar6 + 1;
          *puVar19 = uVar30;
          puVar19 = puVar19 + 1;
        } while (puVar26 != puVar6);
      }
      iVar35 = (int)fVar27 - (int)fVar20;
      if ((int)fVar20 < iVar35) {
        pfVar12 = (float *)(puVar9 + (int)fVar20);
        iVar33 = 0;
        do {
          if ((int)fVar20 * 2 < 0) {
            fVar29 = 0.0;
          }
          else {
            pfVar15 = (float *)param_1[0x2b];
            pfVar4 = (float *)((int)param_1[0x10] + iVar33);
            pfVar16 = pfVar15 + (int)fVar20 * 2 + 1;
            fVar29 = 0.0;
            do {
              fVar8 = *pfVar15;
              pfVar15 = pfVar15 + 1;
              fVar29 = fVar8 * *pfVar4 + fVar29;
              pfVar4 = pfVar4 + 1;
            } while (pfVar16 != pfVar15);
          }
          *pfVar12 = fVar29;
          pfVar12 = pfVar12 + 1;
          iVar33 = iVar33 + 4;
        } while ((float *)(puVar9 + iVar35) != pfVar12);
      }
      if (iVar35 < (int)fVar27) {
        fVar27 = param_1[0x10];
        puVar19 = (undefined4 *)((int)fVar27 + iVar35 * 4);
        puVar9 = puVar9 + iVar35;
        do {
          uVar30 = *puVar19;
          puVar19 = puVar19 + 1;
          *puVar9 = uVar30;
          puVar9 = puVar9 + 1;
        } while ((undefined4 *)((int)fVar27 + iVar11) != puVar19);
      }
      FUN_10011344(param_1[0x1f]);
      FUN_10011344(param_1[0x20],param_1[0x1e],(int)param_1[7] << 2);
      FUN_10011344(param_1[0x21],param_1[0x1e],(int)param_1[7] << 2);
      FUN_10011344(param_1[0x23],param_1[0x1e],(int)param_1[7] << 2);
      FUN_10011344(param_1[0x25],param_1[0x1e],(int)param_1[7] << 2);
      FUN_10011344(param_1[0x29],param_1[0x10],(int)param_1[7] << 2);
      FUN_10011344(param_1[0x28],param_1[0x10],(int)param_1[7] << 2);
      if (0 < (int)param_1[0x1b]) {
        iVar11 = 0;
        do {
          FUN_10011344((int)param_1[0x22] + (int)param_1[7] * iVar11 * 4,param_1[0x10],
                       (int)param_1[7] << 2);
          FUN_10011344((int)param_1[0x24] + (int)param_1[7] * iVar11 * 4,param_1[0x10],
                       (int)param_1[7] << 2);
          iVar11 = iVar11 + 1;
        } while (iVar11 < (int)param_1[0x1b]);
      }
      fVar27 = param_1[7];
      if ((int)fVar27 < 1) {
        fVar20 = param_1[8];
        goto LAB_10015ee8;
      }
      pfVar4 = (float *)param_1[0x10];
      fVar20 = param_1[8];
    }
    fVar29 = DAT_100161c4;
    fVar34 = param_1[0x29];
    fVar32 = param_1[0x2a];
    fVar28 = param_1[0x27];
    fVar22 = param_1[0x11];
    fVar8 = param_1[0x2c];
    pfVar12 = (float *)param_1[0x26];
    iVar11 = 0;
    do {
      fVar38 = pfVar4[iVar11] / (*(float *)((int)fVar34 + iVar11 * 4) + fVar29);
      fVar36 = *(float *)((int)fVar32 + iVar11 * 4);
      fVar37 = fVar38 - 0.0;
      if (fVar38 - 0.0 <= 0.0) {
        fVar37 = 0.0;
      }
      fVar36 = (0.0 - *param_1) * fVar37 + fVar36 * fVar36 * *pfVar12 * *param_1;
      fVar37 = *param_1;
      if (*param_1 < fVar36) {
        fVar37 = fVar36;
      }
      *(float *)((int)fVar28 + iVar11 * 4) = fVar37;
      fVar37 = fVar37 / (fVar37 + 0.0);
      *(float *)((int)fVar22 + iVar11 * 4) = fVar37;
      *(float *)((int)fVar8 + iVar11 * 4) = fVar38 * fVar37;
      iVar11 = iVar11 + 1;
      *pfVar12 = fVar38;
      pfVar12 = pfVar12 + 1;
    } while (iVar11 < (int)fVar27);
  }
LAB_10015ee8:
  fVar29 = param_1[0x1d];
  if (0 < (int)fVar29) {
    pfVar15 = (float *)param_1[0x1e];
    pfVar4 = (float *)param_1[0x10];
    pfVar12 = pfVar15 + (int)fVar29;
    do {
      *pfVar15 = (0.0 - *param_1) * *pfVar4 + *param_1 * *pfVar15;
      pfVar15 = pfVar15 + 1;
      pfVar4 = pfVar4 + 1;
    } while (pfVar12 != pfVar15);
  }
  fVar8 = (float)((int)fVar27 - (int)fVar29);
  if ((int)fVar29 < (int)fVar8) {
    fVar22 = param_1[0x1e];
    pfVar12 = (float *)((int)fVar29 * 4 + (int)fVar22);
    iVar11 = 0;
    do {
      if ((int)fVar29 * 2 < 0) {
        fVar28 = 0.0;
      }
      else {
        pfVar16 = (float *)param_1[0x2b];
        pfVar15 = (float *)((int)param_1[0x10] + iVar11);
        pfVar4 = pfVar16 + (int)fVar29 * 2 + 1;
        fVar28 = 0.0;
        do {
          fVar32 = *pfVar16;
          pfVar16 = pfVar16 + 1;
          fVar28 = fVar32 * *pfVar15 + fVar28;
          pfVar15 = pfVar15 + 1;
        } while (pfVar4 != pfVar16);
      }
      *pfVar12 = *param_1 * *pfVar12 + (0.0 - *param_1) * fVar28;
      pfVar12 = pfVar12 + 1;
      iVar11 = iVar11 + 4;
    } while ((float *)((int)fVar22 + (int)fVar8 * 4) != pfVar12);
  }
  if ((int)fVar8 < (int)fVar27) {
    fVar22 = param_1[0x1e];
    pfVar4 = (float *)((int)fVar22 + (int)fVar8 * 4);
    pfVar12 = (float *)((int)param_1[0x10] + (int)fVar8 * 4);
    do {
      *pfVar4 = (0.0 - *param_1) * *pfVar12 + *param_1 * *pfVar4;
      pfVar4 = pfVar4 + 1;
      pfVar12 = pfVar12 + 1;
    } while ((float *)((int)fVar22 + (int)fVar27 * 4) != pfVar4);
  }
  if (0 < (int)fVar27) {
    pfVar16 = (float *)param_1[0x20];
    pfVar15 = (float *)param_1[0x1e];
    pfVar12 = pfVar15;
    pfVar4 = pfVar16;
    do {
      fVar22 = *pfVar12;
      if (*pfVar4 < *pfVar12) {
        fVar22 = *pfVar4;
      }
      *pfVar4 = fVar22;
      pfVar4 = pfVar4 + 1;
      pfVar12 = pfVar12 + 1;
    } while (pfVar16 + (int)fVar27 != pfVar4);
    pfVar5 = (float *)param_1[0x10];
    fVar22 = param_1[0x2d];
    pfVar12 = pfVar16;
    do {
      while ((*param_1 * *pfVar12 * *param_1 <= *pfVar5 ||
             (*param_1 * *pfVar12 * *param_1 <= *pfVar15))) {
        pfVar18 = pfVar12 + 1;
        *(undefined4 *)((int)pfVar12 + ((int)fVar22 - (int)pfVar16)) = 0;
        pfVar5 = pfVar5 + 1;
        pfVar15 = pfVar15 + 1;
        pfVar12 = pfVar18;
        if (pfVar4 == pfVar18) goto LAB_10016090;
      }
      pfVar18 = pfVar12 + 1;
      *(undefined4 *)((int)pfVar12 + ((int)fVar22 - (int)pfVar16)) = 0;
      pfVar5 = pfVar5 + 1;
      pfVar15 = pfVar15 + 1;
      pfVar12 = pfVar18;
    } while (pfVar4 != pfVar18);
  }
LAB_10016090:
  if (0 < (int)fVar29) {
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  if ((int)fVar29 < (int)fVar8) {
    iVar11 = (int)fVar29 * 2;
    iVar35 = (int)fVar29 << 2;
    fVar22 = param_1[0x1f];
    do {
      if (-1 < iVar11) {
        fVar27 = param_1[0x2b];
        fVar20 = (float)((int)fVar27 + (iVar11 + 1) * 4);
        do {
          fVar27 = (float)((int)fVar27 + 4);
        } while (fVar20 != fVar27);
                    /* WARNING: Bad instruction - Truncating control flow here */
        halt_baddata();
      }
      fVar28 = *(float *)((int)fVar22 + iVar35);
      *(float *)((int)fVar22 + iVar35) = (0.0 - *param_1) * fVar28 + *param_1 * fVar28;
      fVar29 = (float)((int)fVar29 + 1);
      iVar35 = iVar35 + 4;
    } while (fVar29 != fVar8);
  }
  if ((int)fVar8 < (int)fVar27) {
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  if ((int)fVar27 < 1) {
    if (param_1[0x2f] != 2.8026e-45) goto LAB_100163f2;
  }
  else {
    pfVar15 = (float *)param_1[0x21];
    pfVar4 = (float *)param_1[0x1f];
    pfVar12 = pfVar15 + (int)fVar27;
    do {
      fVar29 = *pfVar4;
      if (*pfVar15 < *pfVar4) {
        fVar29 = *pfVar15;
      }
      *pfVar15 = fVar29;
      pfVar15 = pfVar15 + 1;
      pfVar4 = pfVar4 + 1;
    } while (pfVar12 != pfVar15);
    if (param_1[0x2f] != 2.8026e-45) {
      halt_baddata();
    }
  }
  if (0 < (int)fVar27) {
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
LAB_100163f2:
  fVar29 = param_1[0x1c];
  if ((int)fVar20 + 1 == (int)fVar29 * (((int)fVar20 + 1) / (int)fVar29)) {
    iVar11 = (int)fVar20 / (int)fVar29 -
             (int)param_1[0x1b] * (((int)fVar20 / (int)fVar29) / (int)param_1[0x1b]);
    FUN_10011344((int)param_1[0x22] + (int)fVar27 * iVar11 * 4,param_1[0x23],(int)fVar27 << 2);
    FUN_10011344((int)param_1[0x24] + iVar11 * (int)param_1[7] * 4,param_1[0x25],
                 (int)param_1[7] << 2);
    FUN_10011344(param_1[0x20],param_1[0x22],(int)param_1[7] << 2);
    FUN_10011344(param_1[0x21],param_1[0x24],(int)param_1[7] << 2);
    fVar20 = param_1[0x1b];
    fVar27 = param_1[7];
    pfVar12 = (float *)param_1[0x22];
    pfVar4 = (float *)param_1[0x24];
    if (1 < (int)fVar20) {
      fVar29 = 1.4013e-45;
      do {
        pfVar4 = pfVar4 + (int)fVar27;
        pfVar12 = pfVar12 + (int)fVar27;
        if (0 < (int)fVar27) {
          pfVar18 = (float *)param_1[0x20];
          pfVar5 = (float *)param_1[0x21];
          pfVar24 = pfVar18 + (int)fVar27;
          pfVar15 = pfVar4;
          pfVar16 = pfVar12;
          do {
            fVar8 = *pfVar16;
            if (*pfVar18 < *pfVar16) {
              fVar8 = *pfVar18;
            }
            *pfVar18 = fVar8;
            fVar8 = *pfVar15;
            if (*pfVar5 < *pfVar15) {
              fVar8 = *pfVar5;
            }
            pfVar18 = pfVar18 + 1;
            *pfVar5 = fVar8;
            pfVar16 = pfVar16 + 1;
            pfVar5 = pfVar5 + 1;
            pfVar15 = pfVar15 + 1;
          } while (pfVar24 != pfVar18);
        }
        fVar29 = (float)((int)fVar29 + 1);
      } while (fVar29 != fVar20);
    }
    FUN_10011344(param_1[0x23],param_1[0x1e]);
    FUN_10011344(param_1[0x25],param_1[0x1f],(int)param_1[7] << 2);
    fVar27 = param_1[7];
  }
  psVar14 = (short *)param_1[0xf];
  if (0 < (int)fVar27) {
    pfVar12 = (float *)param_1[0x11];
    psVar17 = psVar14;
    do {
      fVar20 = *pfVar12;
      local_24 = (short)(int)((float)(int)*psVar17 * fVar20);
      *psVar17 = local_24;
      local_24 = (short)(int)((float)(int)psVar17[1] * fVar20);
      psVar17[1] = local_24;
      psVar17 = psVar17 + 2;
      pfVar12 = pfVar12 + 1;
    } while (psVar14 + (int)fVar27 * 2 != psVar17);
  }
  fVar27 = param_1[6];
  iVar11 = FUN_1000e2c4(psVar14,(int)fVar27 + 2);
  FUN_1000e28c(psVar14,(int)fVar27 + 2,iVar11);
  gx8002_backup_rfft(DAT_10016638,param_1[0xf],param_1[0xe]);
  FUN_1000e28c(param_1[0xe],param_1[6],(-9 - iVar3) - iVar11);
  fVar27 = param_1[5];
  if (0 < (int)fVar27) {
    fVar28 = param_1[0xe];
    fVar22 = param_1[0xc];
    fVar8 = param_1[0xb];
    fVar29 = param_1[0xd];
    fVar20 = 0.0;
    do {
      uVar13 = (((uint)*(ushort *)((int)fVar8 + (int)fVar20 * 2) +
                 ((int)((uint)*(ushort *)((int)fVar22 + (int)fVar20 * 2) *
                       (uint)*(ushort *)((int)fVar28 + (int)fVar20 * 2)) >> 0xf) & 0xffff) *
                (uint)*(ushort *)((int)fVar29 + (int)fVar20 * 2) & 0x1fffffff) >> 0xe;
      *(ushort *)(param_3 + (int)fVar20 * 2) =
           (ushort)((int)uVar13 < -0x7fff) * -0x7fff +
           (ushort)((int)uVar13 >= -0x7fff) * (short)uVar13;
      fVar20 = (float)((int)fVar20 + 1);
    } while (fVar20 != fVar27);
  }
  if (0 < (int)param_1[3] - (int)fVar27) {
    puVar31 = (undefined2 *)param_1[0xb];
    puVar10 = (uint *)((int)param_1[0xe] + (int)fVar27 * 2);
    puVar21 = (uint *)((int)param_1[0xc] + (int)fVar27 * 2);
    puVar7 = puVar31 + ((int)param_1[3] - (int)fVar27);
    do {
      uVar13 = *puVar10;
      puVar10 = (uint *)((int)puVar10 + 2);
      uVar23 = *puVar21;
      puVar21 = (uint *)((int)puVar21 + 2);
      *puVar31 = (short)((int)((uVar23 & 0xffff) * (uVar13 & 0xffff)) >> 0xf);
      puVar31 = puVar31 + 1;
    } while (puVar7 != puVar31);
  }
  param_1[8] = (float)((int)param_1[8] + 1);
  return;
}

