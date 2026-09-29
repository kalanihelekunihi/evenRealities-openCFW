
undefined8 FUN_005d905c(int param_1,int param_2,int param_3,int param_4,undefined4 param_5)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int local_28;
  int iStack_24;
  
  iVar2 = 0;
  iVar3 = *(int *)(param_1 + 0x18);
  local_28 = *(int *)(param_1 + 0x20);
  iStack_24 = param_4;
  while ((((iVar3 != 0 && (iVar1 = FUN_005d8c00(local_28,param_2), iVar1 == 0)) &&
          (iVar1 = FUN_005d8c00(local_28,param_3), iVar1 == 0)) &&
         (iVar1 = FUN_005d8c00(local_28,param_4), iVar1 == 0))) {
    iVar3 = iVar3 + -1;
    local_28 = local_28 + 0x10;
  }
  if (((((iVar3 != 0) || (iVar2 = FUN_005d8cde(param_1 + 0x18,param_5,&local_28), iVar2 == 0)) &&
       ((param_2 < 0 || (iVar2 = FUN_005d8c3e(local_28,param_2,param_5), iVar2 == 0)))) &&
      ((param_3 < 0 || (iVar2 = FUN_005d8c3e(local_28,param_3,param_5), iVar2 == 0)))) &&
     (-1 < param_4)) {
    iVar2 = FUN_005d8c3e(local_28,param_4,param_5);
  }
  return CONCAT44(local_28,iVar2);
}

