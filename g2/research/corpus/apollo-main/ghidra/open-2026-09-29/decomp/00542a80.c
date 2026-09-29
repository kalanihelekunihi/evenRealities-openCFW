
undefined4 FUN_00542a80(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  double *pdVar2;
  uint uVar3;
  undefined4 uVar4;
  ulonglong in_d0;
  undefined4 extraout_s1;
  uint extraout_s1_00;
  undefined4 extraout_s1_01;
  uint extraout_s1_02;
  undefined4 extraout_s1_03;
  uint extraout_s1_04;
  undefined4 extraout_s1_05;
  uint extraout_s1_06;
  double dVar5;
  undefined4 local_20 [2];
  
  if (((param_1 != 0) && ((in_d0 & 0x7fffffff00000000) != 0 || (int)in_d0 != 0)) &&
     ((((int)(in_d0 >> 0x20) << 1) >> 0x15 != -1 || ((in_d0 & 0xfffff00000000) != 0)))) {
    dVar5 = 1.0;
    if (param_1 < 0) {
      pdVar2 = (double *)((int)&DAT_00542c1c + DAT_00542c1c);
      iVar1 = 8;
      for (uVar3 = -param_1; uVar3 != 0 && iVar1 != 0; uVar3 = uVar3 >> 1) {
        if ((int)(uVar3 << 0x1f) < 0) {
          dVar5 = dVar5 * *pdVar2;
        }
        pdVar2 = pdVar2 + 1;
        iVar1 = iVar1 + -1;
      }
      uVar4 = FUN_004d4138(local_20);
      iVar1 = FUN_004d4208(SUB84((double)CONCAT44(extraout_s1,uVar4) / dVar5,0),local_20[0]);
      in_d0 = CONCAT44(extraout_s1_00,iVar1);
      if (((extraout_s1_00 & 0x7fffffff) != 0 || iVar1 != 0) &&
         (((int)(extraout_s1_00 << 1) >> 0x15 != -1 || ((extraout_s1_00 & 0xfffff) != 0)))) {
        for (; uVar3 != 0; uVar3 = uVar3 - 1) {
          uVar4 = FUN_004d4138(local_20);
          iVar1 = FUN_004d4208(SUB84((double)CONCAT44(extraout_s1_01,uVar4) * DAT_00542d0c,0),
                               local_20[0]);
          in_d0 = CONCAT44(extraout_s1_02,iVar1);
          if (((extraout_s1_02 & 0x7fffffff) == 0 && iVar1 == 0) ||
             (((int)(extraout_s1_02 << 1) >> 0x15 == -1 && ((extraout_s1_02 & 0xfffff) == 0))))
          break;
        }
      }
    }
    else if (0 < param_1) {
      pdVar2 = (double *)((int)&DAT_00542c1c + DAT_00542c1c);
      iVar1 = 8;
      do {
        if (param_1 << 0x1f < 0) {
          dVar5 = dVar5 * *pdVar2;
        }
        param_1 = param_1 >> 1;
        pdVar2 = pdVar2 + 1;
        iVar1 = iVar1 + -1;
      } while ((0 < param_1) && (iVar1 != 0));
      uVar4 = FUN_004d4138(local_20);
      iVar1 = FUN_004d4208(SUB84((double)CONCAT44(extraout_s1_03,uVar4) * dVar5,0),local_20[0]);
      in_d0 = CONCAT44(extraout_s1_04,iVar1);
      if (((extraout_s1_04 & 0x7fffffff) != 0 || iVar1 != 0) &&
         (((int)(extraout_s1_04 << 1) >> 0x15 != -1 || ((extraout_s1_04 & 0xfffff) != 0)))) {
        for (; 0 < param_1; param_1 = param_1 + -1) {
          uVar4 = FUN_004d4138(local_20);
          iVar1 = FUN_004d4208(SUB84((double)CONCAT44(extraout_s1_05,uVar4) * DAT_00542d14,0),
                               local_20[0]);
          in_d0 = CONCAT44(extraout_s1_06,iVar1);
          if (((extraout_s1_06 & 0x7fffffff) == 0 && iVar1 == 0) ||
             (((int)(extraout_s1_06 << 1) >> 0x15 == -1 && ((extraout_s1_06 & 0xfffff) == 0))))
          break;
        }
      }
    }
    if ((((in_d0 & 0x7fffffff00000000) == 0 && (int)in_d0 == 0) ||
        ((((int)(in_d0 >> 0x20) << 1) >> 0x15 == -1 && ((in_d0 & 0xfffff00000000) == 0)))) &&
       (FUN_00439cb2(), param_2 != (uint *)0x0)) {
      *param_2 = *param_2 | 1;
    }
  }
  return param_4;
}

