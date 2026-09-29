
undefined4 validated_byte_copy_430a9c(undefined4 param_1,undefined4 param_2,undefined4 param_3)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = address_validate_430a60(param_2,param_3);
  if (iVar1 == 0) {
    uVar2 = 0xffffffff;
  }
  else {
    FUN_0041568c(param_1,param_2,param_3);
    uVar2 = 0;
  }
  return uVar2;
}

