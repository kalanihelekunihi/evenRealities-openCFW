
undefined8
FUN_0054454a(undefined4 *param_1,undefined4 param_2,undefined4 *param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 *puVar2;
  
  if (*(char *)(param_1 + 6) == '\0') {
    FUN_004733ee(DAT_00544b6c);
    uVar1 = FUN_00585c94(param_1);
    FUN_004733ee(DAT_00544b70,*param_1,uVar1);
    FUN_004733ee(DAT_005450a0,*param_1);
    uVar1 = 0;
    puVar2 = param_3;
  }
  else {
    if (param_1[7] != 0) {
      (*(code *)param_1[7])(param_1);
    }
    puVar2 = param_3 + 4;
    uVar1 = FUN_005444f4(param_1,param_2,*param_3,param_3[1],puVar2,param_4);
    if (param_1[8] != 0) {
      (*(code *)param_1[8])(param_1);
    }
  }
  return CONCAT44(puVar2,uVar1);
}

