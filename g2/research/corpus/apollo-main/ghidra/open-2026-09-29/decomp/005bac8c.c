
undefined * FUN_005bac8c(int param_1)

{
  uint uVar1;
  undefined *puVar2;
  
  uVar1 = param_1 % 0xc;
  if ((int)uVar1 < 0) {
    uVar1 = uVar1 + 0xc;
  }
  if (uVar1 == 0) {
    uVar1 = 0xc;
  }
  puVar2 = PTR_LAB_005bb310;
  if ((uVar1 != 1) &&
     ((uVar1 == 0 ||
      ((((((puVar2 = PTR_DAT_005bb318, uVar1 != 3 && (puVar2 = PTR_DAT_005bb314, 2 < uVar1)) &&
          (puVar2 = PTR_DAT_005bb320, uVar1 != 5)) &&
         ((puVar2 = PTR_DAT_005bb31c, 4 < uVar1 && (puVar2 = PTR_DAT_005bb328, uVar1 != 7)))) &&
        ((puVar2 = PTR_DAT_005bb324, 6 < uVar1 &&
         ((puVar2 = PTR_DAT_005bb330, uVar1 != 9 && (puVar2 = PTR_DAT_005bb32c, 8 < uVar1)))))) &&
       ((puVar2 = PTR_DAT_005bb338, uVar1 != 0xb && (puVar2 = PTR_DAT_005bb334, 10 < uVar1)))))))) {
    puVar2 = PTR_DAT_005bb33c;
  }
  return puVar2;
}

