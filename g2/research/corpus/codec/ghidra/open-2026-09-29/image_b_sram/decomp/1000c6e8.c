
/* WARNING: Control flow encountered bad instruction data */

undefined4 FUN_1000c6e8(float *param_1,float param_2,int param_3)

{
  uint *puVar1;
  float fVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  float *pfVar6;
  float *pfVar7;
  float *pfVar8;
  undefined4 *puVar9;
  float *pfVar10;
  float fVar11;
  int iVar12;
  float *pfVar13;
  float fVar14;
  float *pfVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  
  fVar11 = DAT_1000ca7c;
  fVar2 = param_1[7];
  if (fVar2 != param_2) {
    FUN_10009934(PTR_s_You_must_set_the_beamforming_ang_1000cc6c);
    param_1[0x18] = 0.0;
    return 0xffffffff;
  }
  if (0 < (int)fVar2) {
    pfVar8 = (float *)param_1[0x19];
    do {
      dsp_stub();
      *pfVar8 = ((float)(int)fVar11 / 0.0) * fVar11;
      pfVar8 = pfVar8 + 1;
    } while (param_3 + (int)fVar2 * 2 != param_3);
  }
  param_1[0x18] = 1.4013e-45;
  puVar1 = DAT_1000ca80;
  fVar11 = param_1[6];
  fVar14 = param_1[1];
  fVar2 = param_1[9];
  fVar19 = (float)(int)*param_1 / (float)(int)*param_1;
  fVar20 = *param_1;
  fVar16 = param_1[0xc];
  fVar18 = *param_1;
  iVar3 = (*(code *)(*DAT_1000ca80 & 0xfffffffe))((int)fVar2 << 2);
  iVar12 = (int)fVar14 * 4;
  pfVar8 = (float *)(*(code *)(*puVar1 & 0xfffffffe))(iVar12);
  iVar4 = (*(code *)(*puVar1 & 0xfffffffe))(iVar12);
  iVar5 = (*(code *)(*puVar1 & 0xfffffffe))(iVar12);
  pfVar6 = (float *)(*(code *)(*puVar1 & 0xfffffffe))((int)fVar14 * (int)fVar2 * 4);
  pfVar7 = (float *)(*(code *)(*puVar1 & 0xfffffffe))(iVar12);
  if (((((iVar3 == 0) || (pfVar8 == (float *)0x0)) || (iVar4 == 0)) ||
      ((iVar5 == 0 || (pfVar6 == (float *)0x0)))) || (pfVar7 == (float *)0x0)) {
    FUN_10009934(PTR_s__error___malloc_x_or_y_real_or_y_1000cc68,
                 PTR_s_lvp_vma_lavaliermic_gsc_c_1000cc64,0x127);
    return 0;
  }
  fVar17 = *param_1;
  FUN_1000ded0();
  fVar19 = fVar19 * DAT_1000ca84;
  fVar20 = ((float)(int)fVar20 * DAT_1000ca7c) / 0.0;
  if (fVar16 != 0.0) {
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
  fVar16 = DAT_1000ca84 / (float)(int)fVar14;
  *pfVar7 = 0.0;
  fVar18 = fVar18 * ((fVar19 * fVar17) / 0.0);
  *pfVar7 = fVar16;
  if (2 < (int)fVar14) {
    fVar19 = 2.8026e-45;
    while( true ) {
      pfVar7[(int)fVar19] = (float)(int)fVar19 * fVar16;
      fVar19 = (float)((int)fVar19 + 1);
      if (fVar14 == fVar19) break;
      fVar16 = *pfVar7;
    }
  }
  if (param_1[0x18] == 0.0) {
    if ((int)fVar2 < 1) goto LAB_1000cbdc;
    fVar16 = 0.0;
    pfVar15 = pfVar6;
    do {
      if (0 < (int)fVar14) {
        pfVar10 = pfVar8;
        pfVar13 = pfVar7;
        do {
          fVar19 = *pfVar13;
          pfVar13 = pfVar13 + 1;
          *pfVar10 = (float)(int)fVar16 * fVar20 - fVar19;
          pfVar10 = pfVar10 + 1;
        } while (pfVar7 + (int)fVar14 != pfVar13);
      }
      FUN_1000dee0(pfVar15,pfVar8,fVar14);
      fVar16 = (float)((int)fVar16 + 1);
      pfVar15 = pfVar15 + (int)fVar14;
    } while (fVar2 != fVar16);
  }
  else {
    if ((int)fVar2 < 1) goto LAB_1000cbdc;
    fVar16 = 0.0;
    pfVar15 = pfVar6;
    do {
      if (0 < (int)fVar14) {
        fVar19 = param_1[0x19];
        pfVar10 = pfVar8;
        pfVar13 = pfVar7;
        do {
          fVar20 = *pfVar13;
          pfVar13 = pfVar13 + 1;
          *pfVar10 = *(float *)((int)fVar16 * 4 + (int)fVar19) - fVar20;
          pfVar10 = pfVar10 + 1;
        } while (pfVar7 + (int)fVar14 != pfVar13);
      }
      FUN_1000dee0(pfVar15,pfVar8,fVar14);
      fVar16 = (float)((int)fVar16 + 1);
      pfVar15 = pfVar15 + (int)fVar14;
    } while (fVar2 != fVar16);
  }
  if ((0 < (int)fVar11) && (0 < (int)fVar2)) {
    pfVar7 = (float *)(iVar4 + iVar12);
    if (0 < (int)fVar14) {
      pfVar7 = pfVar8;
      do {
        *pfVar7 = *pfVar6 * (float)(int)fVar2 * fVar18;
        pfVar7 = pfVar7 + 1;
        pfVar6 = pfVar6 + 1;
      } while (pfVar8 + (int)fVar14 != pfVar7);
    }
    FUN_1000dee0(iVar4,pfVar8,fVar14,pfVar7);
    FUN_1000df0c(iVar5,pfVar8,fVar14);
    puVar9 = (undefined4 *)param_1[0x29];
    *puVar9 = 0;
    puVar9[1] = 0;
                    /* WARNING: Bad instruction - Truncating control flow here */
    halt_baddata();
  }
LAB_1000cbdc:
  (*(code *)(puVar1[3] & 0xfffffffe))(iVar3);
  (*(code *)(puVar1[3] & 0xfffffffe))(pfVar8);
  (*(code *)(puVar1[3] & 0xfffffffe))(iVar4);
  (*(code *)(puVar1[3] & 0xfffffffe))(iVar5);
  (*(code *)(puVar1[3] & 0xfffffffe))(pfVar6);
  (*(code *)(puVar1[3] & 0xfffffffe))(pfVar7);
  return 0;
}

