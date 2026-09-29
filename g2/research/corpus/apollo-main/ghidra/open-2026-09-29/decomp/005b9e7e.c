
undefined * FUN_005b9e7e(int param_1)

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
  puVar2 = DAT_005ba9dc;
  if ((uVar1 != 1) &&
     ((uVar1 == 0 ||
      ((((((puVar2 = PTR_DAT_005baa28, uVar1 != 3 && (puVar2 = DAT_005ba9e0, 2 < uVar1)) &&
          (puVar2 = PTR_DAT_005baa30, uVar1 != 5)) &&
         ((puVar2 = PTR_DAT_005baa2c, 4 < uVar1 && (puVar2 = PTR_DAT_005baa38, uVar1 != 7)))) &&
        ((puVar2 = PTR_DAT_005baa34, 6 < uVar1 &&
         ((puVar2 = PTR_DAT_005baa40, uVar1 != 9 && (puVar2 = PTR_DAT_005baa3c, 8 < uVar1)))))) &&
       ((puVar2 = PTR_DAT_005baa80, uVar1 != 0xb && (puVar2 = PTR_DAT_005baa7c, 10 < uVar1)))))))) {
    puVar2 = PTR_DAT_005baa84;
  }
  return puVar2;
}

