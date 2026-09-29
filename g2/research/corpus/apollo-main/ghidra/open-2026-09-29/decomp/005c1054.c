
undefined8 FUN_005c1054(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  FUN_005c1048(param_1,0x40);
  *(undefined4 *)(param_1 + 0x20) = 1;
  *(undefined1 *)(param_1 + 0x3c) = 0xff;
  local_10 = FUN_004410a6();
  FUN_00439be4(param_1 + 0x1c,&local_10,3);
  *(undefined4 *)(param_1 + 0x14) = 0x40;
  return CONCAT44(uStack_c,local_10);
}

