
undefined4 FUN_0041cd1a(undefined1 param_1,undefined1 param_2)

{
  undefined4 uVar1;
  
  if (*(int *)(DAT_0041d11c + 4) == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (**(code **)(DAT_0041d11c + 4))(param_1,param_2);
  }
  return uVar1;
}

