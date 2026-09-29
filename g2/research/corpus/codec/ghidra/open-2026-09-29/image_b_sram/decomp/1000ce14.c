
/* WARNING: Control flow encountered bad instruction data */

int * FUN_1000ce14(int param_1,int param_2,int param_3,int param_4,int param_5,int param_6,
                  int param_7,undefined4 param_8,int param_9,undefined4 *param_10)

{
  uint *puVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  int *piVar5;
  int *piVar6;
  undefined4 *puVar8;
  int *piVar9;
  float *pfVar10;
  undefined4 *puVar11;
  int *piVar12;
  float *pfVar13;
  int iVar14;
  int iVar15;
  int iVar16;
  int iVar17;
  int iVar18;
  int *piVar19;
  float fVar20;
  int in_vr3;
  int *piVar7;
  
  puVar1 = DAT_1000d17c;
  piVar2 = (int *)(*(code *)(*DAT_1000d17c & 0xfffffffe))(0xdc);
  piVar2[2] = 3;
  piVar2[3] = 0x200;
  piVar2[5] = 0x200;
  piVar2[6] = 0x101;
  piVar2[0x12] = 5;
  piVar2[0x13] = 9;
  piVar2[0x14] = 0x3b;
  piVar2[0x15] = 0x33;
  piVar2[4] = 0x100;
  *piVar2 = param_1;
  *piVar2 = in_vr3;
  *piVar2 = in_vr3;
  *piVar2 = in_vr3;
  *piVar2 = in_vr3;
  piVar2[0x35] = 100;
  piVar2[1] = param_2;
  piVar2[7] = param_3;
  piVar2[0xc] = param_4;
  piVar2[0xe] = param_5;
  piVar2[0x10] = param_6;
  piVar2[0x11] = param_7;
  piVar2[0x16] = param_9;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(400);
  iVar17 = param_3 * 4;
  piVar2[0x36] = iVar3;
  piVar2[0x18] = 0;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(iVar17);
  piVar2[0x19] = iVar3;
  if (piVar2[0xc] + piVar2[0xe] != 1) {
    FUN_10009934(PTR_s__error___please_set_linear_array_10014157_1_1000d184,
                 PTR_s_lvp_vma_lavaliermic_gsc_c_1000d180,0x443);
  }
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(0x800);
  piVar2[0x1c] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(0xc00);
  piVar2[0x1d] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(6);
  piVar2[0x25] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(param_2 * param_3 * 0x808);
  piVar2[0x29] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(param_3 * piVar2[0x12] * 2);
  piVar2[0x2b] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(iVar17);
  piVar2[0x2c] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(8);
  piVar2[0x2d] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(param_3 * 0x404);
  piVar2[0x2e] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(param_2 << 3);
  piVar2[0x2f] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(param_2 * (param_2 + -1) * 8);
  iVar14 = param_3 * 0x101 * (param_2 + -1) * 8;
  piVar2[0x30] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(iVar14);
  piVar2[0x31] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(iVar17);
  piVar2[0x2a] = iVar3;
  iVar3 = (*(code *)(*puVar1 & 0xfffffffe))(param_9 * 4);
  piVar2[0x17] = iVar3;
  piVar2[9] = param_3;
  if (param_4 == 0) {
    piVar2[8] = 0x168 / param_3;
    fVar20 = ((float)*piVar2 / (float)param_3) * DAT_1000d1f0;
    if (0 < param_3) {
      pfVar13 = (float *)piVar2[0x2a];
      pfVar10 = pfVar13 + param_3;
      do {
        *pfVar13 = fVar20;
        pfVar13 = pfVar13 + 1;
      } while (pfVar10 != pfVar13);
    }
  }
  else {
    if (param_3 == 1) {
      piVar2[8] = 0;
    }
    else {
      piVar2[8] = 0xb4 / (param_3 + -1);
      if (param_3 < 1) goto LAB_1000cfd8;
    }
    uVar4 = DAT_1000d188;
    iVar3 = piVar2[0x2a];
    iVar17 = 0;
    do {
      *(undefined4 *)(iVar3 + iVar17 * 4) = uVar4;
      iVar17 = iVar17 + 1;
    } while (iVar17 < param_3);
  }
LAB_1000cfd8:
  FUN_100113c4(piVar2[0x36],0,piVar2[0x35] << 2);
  FUN_100113c4(piVar2[0x2e],0,param_3 * 0x404);
  FUN_100113c4(piVar2[0x31],0,iVar14);
  FUN_100113c4(piVar2[0x2b],0,param_3 * piVar2[0x12] * 2);
  uVar4 = DAT_1000d18c;
  if (0 < param_3 * 0x101) {
    puVar11 = (undefined4 *)piVar2[0x2e];
    puVar8 = puVar11 + param_3 * 0x101;
    do {
      *puVar11 = uVar4;
      puVar11 = puVar11 + 1;
    } while (puVar8 != puVar11);
  }
  if (0 < param_9) {
    puVar11 = (undefined4 *)piVar2[0x17];
    puVar8 = param_10 + param_9;
    do {
      uVar4 = *param_10;
      param_10 = param_10 + 1;
      *puVar11 = uVar4;
      puVar11 = puVar11 + 1;
    } while (puVar8 != param_10);
  }
  iVar3 = piVar2[3];
  if (iVar3 < 1) {
    iVar18 = piVar2[2];
    iVar15 = piVar2[4];
    iVar14 = iVar18 + 2;
    iVar17 = iVar14 * iVar15;
    iVar16 = ((iVar3 - iVar15) + iVar17) * 4;
    piVar5 = (int *)(*(code *)(*puVar1 & 0xfffffffe))(iVar16);
    if (piVar5 == (int *)0x0) {
      FUN_10009934(PTR_s__error___malloc_wtmp_failed___s__1000d1f8,
                   PTR_s_lvp_vma_lavaliermic_gsc_c_1000d1f4,0x1bb);
    }
    else {
      FUN_100113c4(piVar5,0,iVar16);
      if ((-2 < iVar18) && (0 < iVar3)) {
        piVar19 = (int *)piVar2[0x1c];
        iVar16 = 0;
        piVar6 = piVar19;
        piVar9 = piVar5;
        piVar12 = piVar5;
        do {
          do {
            piVar7 = piVar6 + 1;
            *piVar9 = (*piVar6 * *piVar6 >> 0xf) + *piVar9;
            piVar6 = piVar7;
            piVar9 = piVar9 + 1;
          } while (piVar19 + iVar3 != piVar7);
          iVar16 = iVar16 + 1;
          piVar9 = piVar12 + iVar15;
          piVar6 = piVar19;
          piVar12 = piVar9;
        } while (iVar16 != iVar14);
      }
      iVar17 = iVar17 + iVar15 * -2;
      if (0 < iVar17) {
        piVar12 = (int *)piVar2[0x1d];
        piVar9 = piVar5 + 0x100;
        piVar6 = piVar12 + iVar17;
        do {
          iVar3 = *piVar9;
          piVar9 = piVar9 + 1;
          *piVar12 = (int)((0.0 / (float)iVar3) * 0.0);
          piVar12 = piVar12 + 1;
        } while (piVar6 != piVar12);
      }
      (*(code *)(puVar1[3] & 0xfffffffe))(piVar5);
    }
    return piVar2;
  }
  FUN_1000ded0();
                    /* WARNING: Bad instruction - Truncating control flow here */
  halt_baddata();
}

