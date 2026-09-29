
undefined1 GattValueUpdate(short *param_1,int param_2)

{
  undefined1 uVar1;
  
  uVar1 = 0;
  if (*(short *)(param_2 + 10) == *param_1) {
    FUN_00533630(param_2);
  }
  else {
    uVar1 = 10;
  }
  return uVar1;
}

