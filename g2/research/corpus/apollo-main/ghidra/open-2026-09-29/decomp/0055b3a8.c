
undefined8 FUN_0055b3a8(int param_1,undefined2 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_18;
  undefined4 uStack_14;
  
  local_18 = param_3;
  uStack_14 = param_4;
  FUN_0043c0e4(&local_18,2,0);
  if ((param_1 == 0) || (param_2 == (undefined2 *)0x0)) {
    iVar1 = -1;
  }
  else {
    iVar1 = (**(code **)(param_1 + 4))(6,&local_18,2);
    if (iVar1 == 0) {
      *param_2 = (undefined2)local_18;
      iVar1 = 0;
    }
  }
  return CONCAT44(local_18,iVar1);
}

