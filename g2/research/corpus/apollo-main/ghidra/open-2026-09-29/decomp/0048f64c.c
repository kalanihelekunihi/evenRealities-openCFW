
undefined8 FUN_0048f64c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  iVar1 = FUN_0048f5ae(param_1,&local_10);
  if (iVar1 == 0) {
    uVar2 = 0;
  }
  else {
    uVar2 = FUN_0048f3be(param_1,0,local_10);
  }
  return CONCAT44(local_10,uVar2);
}

