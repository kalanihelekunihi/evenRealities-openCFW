
undefined8 FUN_00489f5e(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  FUN_00489ec8(param_1,100);
  *(undefined1 *)(param_1 + 0x50) = 0xff;
  local_10 = FUN_004410a6();
  FUN_00439be4(param_1 + 0x24,&local_10,3);
  *(undefined4 *)(param_1 + 0x4c) = 0xffffffff;
  *(undefined4 *)(param_1 + 0x20) = DAT_0048a944;
  *(undefined4 *)(param_1 + 0x3c) = 0xffff;
  *(undefined4 *)(param_1 + 0x40) = 0xffff;
  local_10 = FUN_004410a6();
  FUN_00439be4(param_1 + 0x44,&local_10,3);
  local_10 = FUN_00488290(5);
  FUN_00439be4(param_1 + 0x47,&local_10,3);
  *(undefined1 *)(param_1 + 0x52) = 0;
  *(undefined4 *)(param_1 + 0x14) = 100;
  return CONCAT44(uStack_c,local_10);
}

