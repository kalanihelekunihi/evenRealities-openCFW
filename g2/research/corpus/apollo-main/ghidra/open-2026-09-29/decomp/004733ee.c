
undefined8 FUN_004733ee(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uStack_c;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  uVar2 = DAT_00473470;
  piVar1 = DAT_0047345c;
  if (*DAT_0047345c == 0) {
    uVar3 = 0;
  }
  else {
    uStack_c = param_2;
    uStack_8 = param_3;
    uStack_4 = param_4;
    uVar3 = FUN_00473036(DAT_00473470,param_1,&uStack_c);
    (*(code *)*piVar1)(uVar2);
  }
  return CONCAT44(param_4,uVar3);
}

