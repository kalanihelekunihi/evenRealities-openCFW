
undefined1 FUN_0054503a(undefined4 *param_1,undefined4 param_2,undefined4 *param_3)

{
  undefined1 uVar1;
  undefined4 uVar2;
  
  if (*(char *)(param_1 + 6) == '\0') {
    FUN_004733ee(DAT_00545534);
    uVar2 = FUN_00585c94(param_1);
    FUN_004733ee(DAT_00545538,*param_1,uVar2);
    FUN_004733ee(DAT_00545554,*param_1);
    uVar1 = 8;
  }
  else {
    if (param_1[7] != 0) {
      (*(code *)param_1[7])(param_1);
    }
    uVar1 = FUN_00544f6c(param_1,param_2,*param_3,param_3[1]);
    if (param_1[8] != 0) {
      (*(code *)param_1[8])(param_1);
    }
  }
  return uVar1;
}

