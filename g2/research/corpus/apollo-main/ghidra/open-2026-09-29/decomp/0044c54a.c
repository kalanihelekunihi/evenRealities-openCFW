
undefined8 FUN_0044c54a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 uVar2;
  
  cVar1 = FUN_0044b8de(param_1,param_2);
  if (cVar1 != '\0') {
    uVar2 = FUN_0044b8d0(param_1,param_2);
    uVar2 = FUN_00440fde(uVar2,cVar1);
    param_3 = FUN_00482ef6(param_3,uVar2);
  }
  return CONCAT44(param_4,param_3);
}

