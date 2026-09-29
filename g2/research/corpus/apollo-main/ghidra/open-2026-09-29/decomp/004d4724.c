
undefined8 FUN_004d4724(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  
  FUN_004d47fa(param_1);
  FUN_004420d0();
  iVar1 = *(int *)(param_1 + 8);
  *(undefined4 *)(param_1 + 8) = 0;
  if (iVar1 == 0) {
    *(undefined4 *)(param_1 + 4) = 1;
  }
  FUN_004420e8();
  local_10 = param_4;
  if (iVar1 != 0) {
    local_10 = 0;
    FUN_00455c48(iVar1,0,0,2);
  }
  return CONCAT44(local_10,1);
}

