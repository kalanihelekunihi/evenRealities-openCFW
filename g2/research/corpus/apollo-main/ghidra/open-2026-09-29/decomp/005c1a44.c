
undefined4 FUN_005c1a44(undefined4 param_1,int param_2)

{
  undefined4 unaff_r7;
  
  *(undefined4 *)(param_2 + 0x38) = 0;
  *(undefined4 *)(param_2 + 0x3c) = 0;
  *(undefined4 *)(param_2 + 0x40) = 0xffff;
  *(undefined4 *)(param_2 + 0x30) = 0;
  *(undefined4 *)(param_2 + 0x34) = 0;
  *(undefined4 *)(param_2 + 0x2c) = 0;
  *(uint *)(param_2 + 0x44) = *(uint *)(param_2 + 0x44) & 0xfffffffe;
  *(uint *)(param_2 + 0x44) = *(uint *)(param_2 + 0x44) & 0xfffffffd;
  FUN_005c16d8(param_2,DAT_005c25c4);
  return unaff_r7;
}

