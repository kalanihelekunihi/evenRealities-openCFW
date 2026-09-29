
undefined * FUN_005bad10(int param_1)

{
  uint uVar1;
  undefined *puVar2;
  
  if (param_1 < 0) {
    param_1 = 0;
  }
  if (0x3b < param_1) {
    param_1 = 0x3b;
  }
  uVar1 = param_1 / 5;
  if (uVar1 == 0) {
    uVar1 = 0xc;
  }
  puVar2 = PTR_DAT_005bb340;
  if ((uVar1 != 1) &&
     ((uVar1 == 0 ||
      ((((((puVar2 = PTR_DAT_005bb348, uVar1 != 3 && (puVar2 = PTR_DAT_005bb344, 2 < uVar1)) &&
          (puVar2 = PTR_DAT_005bb350, uVar1 != 5)) &&
         ((puVar2 = PTR_DAT_005bb34c, 4 < uVar1 && (puVar2 = PTR_DAT_005bb358, uVar1 != 7)))) &&
        ((puVar2 = PTR_DAT_005bb354, 6 < uVar1 &&
         ((puVar2 = PTR_DAT_005bb360, uVar1 != 9 && (puVar2 = PTR_DAT_005bb35c, 8 < uVar1)))))) &&
       ((puVar2 = PTR_DAT_005bb368, uVar1 != 0xb && (puVar2 = PTR_DAT_005bb364, 10 < uVar1)))))))) {
    puVar2 = DAT_005bbafc;
  }
  return puVar2;
}

