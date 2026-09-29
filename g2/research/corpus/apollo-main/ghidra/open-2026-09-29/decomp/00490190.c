
undefined8
FUN_00490190(undefined4 param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  iVar1 = FUN_0048f3be(param_1,&local_10,4);
  if (iVar1 != 0) {
    *param_2 = local_10;
  }
  return CONCAT44(local_10,(uint)(iVar1 != 0));
}

