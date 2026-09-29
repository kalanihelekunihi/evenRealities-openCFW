
undefined8 FUN_0049012c(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  iVar1 = FUN_0048f5ae(param_1,&local_10);
  if (iVar1 != 0) {
    *(bool *)param_2 = local_10 != 0;
  }
  return CONCAT44(local_10,(uint)(iVar1 != 0));
}

