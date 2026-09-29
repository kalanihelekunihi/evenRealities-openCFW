
undefined4 cff_driver_init(int param_1)

{
  uint uVar1;
  undefined1 auStack_8 [4];
  undefined1 auStack_4 [4];
  
  *(undefined4 *)(param_1 + 0x1c) = 1;
  *(undefined1 *)(param_1 + 0x20) = 1;
  *(undefined4 *)(param_1 + 0x24) = 500;
  *(undefined4 *)(param_1 + 0x28) = 400;
  *(undefined4 *)(param_1 + 0x2c) = 1000;
  *(undefined4 *)(param_1 + 0x30) = 0x113;
  *(undefined4 *)(param_1 + 0x34) = 0x683;
  *(undefined4 *)(param_1 + 0x38) = 0x113;
  *(undefined4 *)(param_1 + 0x3c) = 0x91d;
  *(undefined4 *)(param_1 + 0x40) = 0;
  uVar1 = (uint)auStack_8 ^ (uint)auStack_4 ^ *(uint *)(param_1 + 8);
  *(uint *)(param_1 + 0x44) = uVar1 ^ uVar1 >> 10 ^ uVar1 >> 0x14;
  if (*(int *)(param_1 + 0x44) < 0) {
    *(int *)(param_1 + 0x44) = -*(int *)(param_1 + 0x44);
  }
  else if (*(int *)(param_1 + 0x44) == 0) {
    *(undefined4 *)(param_1 + 0x44) = DAT_005b010c;
  }
  return 0;
}

