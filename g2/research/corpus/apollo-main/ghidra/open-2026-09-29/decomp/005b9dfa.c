
undefined * FUN_005b9dfa(int param_1)

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
  puVar2 = PTR_LAB_005ba904;
  if ((uVar1 != 1) &&
     ((uVar1 == 0 ||
      ((((((puVar2 = PTR_DAT_005ba90c, uVar1 != 3 && (puVar2 = PTR_DAT_005ba908, 2 < uVar1)) &&
          (puVar2 = PTR_DAT_005ba914, uVar1 != 5)) &&
         ((puVar2 = PTR_DAT_005ba910, 4 < uVar1 && (puVar2 = PTR_DAT_005ba91c, uVar1 != 7)))) &&
        ((puVar2 = PTR_DAT_005ba918, 6 < uVar1 &&
         ((puVar2 = PTR_DAT_005ba924, uVar1 != 9 && (puVar2 = PTR_DAT_005ba920, 8 < uVar1)))))) &&
       ((puVar2 = PTR_DAT_005ba92c, uVar1 != 0xb && (puVar2 = PTR_DAT_005ba928, 10 < uVar1)))))))) {
    puVar2 = PTR_DAT_005baa78;
  }
  return puVar2;
}

