
undefined4 input_tick_read(undefined4 *param_1)

{
  undefined4 uVar1;
  undefined4 local_48 [16];
  
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = 0xffffffff;
  }
  else {
    FUN_00480d72(1,local_48);
    *param_1 = local_48[0];
    uVar1 = 0;
  }
  return uVar1;
}

