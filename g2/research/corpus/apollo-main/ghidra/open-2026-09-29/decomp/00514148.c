
undefined8 FUN_00514148(undefined4 param_1,uint param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = FUN_00514050();
  if ((param_2 < *(uint *)(iVar1 + 0x14)) ||
     ((uint)(*(int *)(iVar1 + 0x10) + *(int *)(iVar1 + 0x14)) < param_3 + param_2)) {
    uVar2 = 0;
  }
  else {
    uVar2 = 1;
  }
  return CONCAT44(param_4,uVar2);
}

