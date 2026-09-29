
/* WARNING: Removing unreachable block (ram,0x00591a9a) */

undefined8
service_algo_cross_correlation
          (int param_1,int param_2,int param_3,int param_4,undefined8 *param_5,double *param_6,
          double *param_7,double *param_8)

{
  longlong lVar1;
  longlong lVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  bool bVar10;
  uint in_fpscr;
  undefined4 uVar11;
  undefined4 uVar12;
  double in_d0;
  undefined4 extraout_s1;
  undefined4 extraout_s1_00;
  double dVar13;
  undefined4 extraout_s1_01;
  undefined4 extraout_s1_02;
  undefined4 extraout_s1_03;
  undefined4 extraout_s1_04;
  double dVar14;
  undefined4 extraout_s1_05;
  undefined4 extraout_s1_06;
  undefined4 extraout_s1_07;
  double dVar15;
  double in_d3;
  double in_d4;
  
  if (param_3 < 1) {
    if (param_5 != (undefined8 *)0x0) {
      uVar11 = service_algo_quiet_nan();
      *param_5 = CONCAT44(extraout_s1,uVar11);
    }
    if (param_6 != (double *)0x0) {
      uVar11 = service_algo_quiet_nan();
      *param_6 = (double)CONCAT44(extraout_s1_00,uVar11);
    }
    if (param_7 != (double *)0x0) {
      *(undefined4 *)param_7 = 0;
      *(undefined4 *)((int)param_7 + 4) = 0;
    }
    if (param_8 != (double *)0x0) {
      *(undefined4 *)param_8 = 0;
      *(undefined4 *)((int)param_8 + 4) = 0;
    }
  }
  else {
    uVar5 = 0;
    iVar8 = 0;
    for (iVar9 = 0; iVar9 < param_3; iVar9 = iVar9 + 1) {
      uVar3 = (uint)*(short *)(param_2 + iVar9 * 2);
      uVar6 = (uint)((ulonglong)uVar3 * (ulonglong)uVar3);
      bVar10 = CARRY4(uVar5,uVar6);
      uVar5 = uVar5 + uVar6;
      iVar8 = iVar8 + ((int)uVar3 >> 0x1f) * uVar3 +
                      uVar3 * ((int)uVar3 >> 0x1f) +
                      (int)((ulonglong)uVar3 * (ulonglong)uVar3 >> 0x20) + (uint)bVar10;
    }
    dVar15 = DAT_00591cd0;
    dVar13 = DAT_00591cd0;
    if (0 < param_3) {
      dVar13 = (double)FUN_0059c7ac();
      dVar15 = (double)VectorSignedToFloat(param_3,(byte)(in_fpscr >> 0x16) & 3);
      uVar11 = FUN_0059c800(SUB84(dVar13 / dVar15,0));
      dVar13 = (double)FUN_0059c7ac(uVar5,iVar8);
      dVar15 = (double)VectorSignedToFloat(param_3,(byte)(in_fpscr >> 0x16) & 3);
      uVar12 = FUN_0059c800(SUB84(dVar13 / dVar15,0));
      dVar15 = (double)CONCAT44(extraout_s1_02,uVar12);
      dVar13 = (double)CONCAT44(extraout_s1_01,uVar11);
    }
    uVar5 = in_fpscr & 0xfffffff;
    if (dVar13 <= dVar15) {
      dVar13 = dVar15;
    }
    if (param_8 != (double *)0x0) {
      *param_8 = dVar13;
    }
    if (in_d3 <= dVar13) {
      if (param_4 < 1) {
        param_4 = 8;
      }
      iVar8 = -param_4;
      iVar7 = param_4 * 2 + 1;
      lVar2 = -0x8000000000000000;
      dVar13 = DAT_00591cd0;
      iVar9 = DAT_00591cc4;
      while( true ) {
        if (param_4 < iVar8) break;
        lVar1 = 0;
        if (iVar8 < 0) {
          for (iVar4 = 0; iVar4 < param_3 + iVar8; iVar4 = iVar4 + 1) {
            lVar1 = (longlong)(int)*(short *)(param_2 + iVar4 * 2) *
                    (longlong)(int)*(short *)(param_1 + (iVar4 - iVar8) * 2) + lVar1;
          }
        }
        else {
          lVar1 = 0;
          for (iVar4 = 0; iVar4 < param_3 - iVar8; iVar4 = iVar4 + 1) {
            lVar1 = (longlong)(int)*(short *)(param_2 + (iVar8 + iVar4) * 2) *
                    (longlong)(int)*(short *)(param_1 + iVar4 * 2) + lVar1;
          }
        }
        if (lVar2 < lVar1) {
          iVar9 = iVar8;
          lVar2 = lVar1;
        }
        dVar15 = (double)FUN_0059c7ac();
        dVar13 = ABS(dVar15) + dVar13;
        iVar8 = iVar8 + 1;
      }
      dVar14 = (double)FUN_0059c7ac((int)lVar2,(int)((ulonglong)lVar2 >> 0x20));
      dVar15 = DAT_00591cd0;
      if (0 < iVar7) {
        dVar15 = (double)VectorSignedToFloat(iVar7,(byte)(uVar5 >> 0x16) & 3);
        dVar15 = dVar13 / dVar15;
      }
      dVar13 = DAT_00591cd0;
      if (0.0 < dVar15) {
        dVar13 = dVar14 / (dVar15 + DAT_00591cc8);
      }
      if (param_7 != (double *)0x0) {
        *param_7 = dVar13;
      }
      if (in_d4 <= dVar13) {
        dVar13 = (double)VectorSignedToFloat(iVar9,(byte)((uVar5 & 0xfffffff) >> 0x16) & 3);
        uVar11 = service_algo_delay_to_angle(SUB84(dVar13 / in_d0,0));
        if (param_5 != (undefined8 *)0x0) {
          *param_5 = CONCAT44(extraout_s1_07,uVar11);
        }
        if (param_6 != (double *)0x0) {
          *param_6 = dVar13 / in_d0;
        }
      }
      else {
        if (param_5 != (undefined8 *)0x0) {
          uVar11 = service_algo_quiet_nan();
          *param_5 = CONCAT44(extraout_s1_05,uVar11);
        }
        if (param_6 != (double *)0x0) {
          uVar11 = service_algo_quiet_nan();
          *param_6 = (double)CONCAT44(extraout_s1_06,uVar11);
        }
      }
    }
    else {
      if (param_5 != (undefined8 *)0x0) {
        uVar11 = service_algo_quiet_nan();
        *param_5 = CONCAT44(extraout_s1_03,uVar11);
      }
      if (param_6 != (double *)0x0) {
        uVar11 = service_algo_quiet_nan();
        *param_6 = (double)CONCAT44(extraout_s1_04,uVar11);
      }
      if (param_7 != (double *)0x0) {
        *(undefined4 *)param_7 = 0;
        *(undefined4 *)((int)param_7 + 4) = 0;
      }
    }
  }
  return CONCAT44(param_3,param_2);
}

