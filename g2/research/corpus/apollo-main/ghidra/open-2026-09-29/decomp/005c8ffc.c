
undefined8 FUN_005c8ffc(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  local_10 = FUN_00482faa();
  FUN_00439be4(param_2 + 0x2c,&local_10,3);
  *(undefined1 *)(param_2 + 0x2f) = 0xff;
  return CONCAT44(uStack_c,local_10);
}

