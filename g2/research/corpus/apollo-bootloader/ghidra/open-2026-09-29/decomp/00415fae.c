
undefined8 FUN_00415fae(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uStack_c;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  uVar2 = DAT_00415ff0;
  piVar1 = DAT_00415fdc;
  if (*DAT_00415fdc == 0) {
    uVar3 = 0;
  }
  else {
    uStack_c = param_2;
    uStack_8 = param_3;
    uStack_4 = param_4;
    uVar3 = FUN_00415bf6(DAT_00415ff0,param_1,&uStack_c);
    (*(code *)*piVar1)(uVar2);
  }
  return CONCAT44(param_4,uVar3);
}

