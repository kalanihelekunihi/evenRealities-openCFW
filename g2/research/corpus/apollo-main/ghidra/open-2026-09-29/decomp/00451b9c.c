
undefined4 FUN_00451b9c(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  
  local_10 = param_4;
  FUN_00451b90(param_1,0x70);
  local_10 = FUN_00441094();
  FUN_00439be4(param_1 + 0x21,&local_10,3);
  local_10 = FUN_00441094();
  FUN_00439be4(param_1 + 0x24,&local_10,3);
  local_10 = FUN_004410a6();
  FUN_00439be4(param_1 + 0x29,&local_10,3);
  *(undefined1 *)(param_1 + 0x2d) = 0xff;
  *(undefined1 *)(param_1 + 0x2e) = 2;
  local_10 = FUN_004410a6();
  FUN_00439be4(param_1 + 0x3e,&local_10,3);
  local_10 = FUN_004410a6();
  FUN_00439be4(param_1 + 0x59,&local_10,3);
  *(undefined4 *)(param_1 + 0x34) = DAT_004522a8;
  *(undefined1 *)(param_1 + 0x20) = 0xff;
  *(undefined1 *)(param_1 + 0x3b) = 0xff;
  *(undefined1 *)(param_1 + 0x58) = 0xff;
  *(undefined1 *)(param_1 + 0x48) = 0xff;
  *(undefined1 *)(param_1 + 0x6c) = 0xff;
  *(byte *)(param_1 + 0x49) = *(byte *)(param_1 + 0x49) & 0xe0 | 0xf;
  return local_10;
}

