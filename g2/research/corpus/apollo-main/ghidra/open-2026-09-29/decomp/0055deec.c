
undefined8 FUN_0055deec(uint *param_1,char param_2,uint *param_3,uint *param_4,uint *param_5)

{
  undefined4 uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  uint uVar9;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  
  uVar11 = *param_4;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055e1f8)) {
    uVar1 = 2;
  }
  else if (param_5 == (uint *)0x0) {
    uVar1 = 6;
  }
  else {
    *param_4 = 0;
    if (param_3 == (uint *)0x0) {
      do {
        uVar2 = FUN_0055de7c(*DAT_0055e220,
                             (DAT_0055e200[(*DAT_0055e220 & 0x7fffffff) >> 0x1c] & 0xfff) >> 8 != 8)
        ;
        param_5[1] = (uVar2 & 0x7fffffff) >> 0x1c;
        if (param_2 == '\0') {
          uVar10 = (uVar2 & 0xfffff) >> 6;
        }
        else {
          uVar10 = uVar2 & 0xfffff;
        }
        *param_5 = uVar10;
        param_5 = param_5 + 2;
        *param_4 = *param_4 + 1;
      } while (((uVar2 & 0xfffffff) >> 0x14 != 0) && (*param_4 < uVar11));
    }
    else {
      uVar2 = *DAT_0055e200;
      if ((*DAT_0055e224 & 0xfff) >> 8 == 8) {
        uVar10 = 2;
      }
      else {
        uVar10 = 0;
      }
      if ((*DAT_0055e228 & 0xfff) >> 8 == 8) {
        uVar3 = 4;
      }
      else {
        uVar3 = 0;
      }
      if ((*DAT_0055e22c & 0xfff) >> 8 == 8) {
        uVar4 = 8;
      }
      else {
        uVar4 = 0;
      }
      if ((*DAT_0055e230 & 0xfff) >> 8 == 8) {
        uVar5 = 0x10;
      }
      else {
        uVar5 = 0;
      }
      if ((*DAT_0055e234 & 0xfff) >> 8 == 8) {
        uVar6 = 0x20;
      }
      else {
        uVar6 = 0;
      }
      if ((*DAT_0055e238 & 0xfff) >> 8 == 8) {
        uVar7 = 0x40;
      }
      else {
        uVar7 = 0;
      }
      if ((*DAT_0055e23c & 0xfff) >> 8 == 8) {
        uVar8 = 0x80;
      }
      else {
        uVar8 = 0;
      }
      do {
        uVar12 = (*param_3 & 0x7fffffff) >> 0x1c;
        uVar9 = FUN_0055de7c(*param_3 & 0xfffff,
                             (uVar8 | uVar7 | uVar6 | uVar5 | uVar4 | uVar3 | uVar10 | (uVar2 & 
                                                  0xfff) >> 8 == 8) >> uVar12 & 1 ^ 1);
        *param_5 = (uVar9 & 0xfffff) >> 6;
        param_5[1] = uVar12;
        param_3 = param_3 + 1;
        param_5 = param_5 + 2;
        *param_4 = *param_4 + 1;
      } while (*param_4 < uVar11);
    }
    uVar1 = 0;
  }
  return CONCAT44(param_4,uVar1);
}

