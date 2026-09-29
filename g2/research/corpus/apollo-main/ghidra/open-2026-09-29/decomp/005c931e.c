
undefined4 FUN_005c931e(undefined4 param_1,int param_2)

{
  undefined4 unaff_r7;
  
  *(undefined4 *)(param_2 + 0x30) = 0;
  *(undefined4 *)(param_2 + 0x2c) = 0;
  *(uint *)(param_2 + 0x34) = *(uint *)(param_2 + 0x34) & 0xfffffffe;
  *(uint *)(param_2 + 0x34) = *(uint *)(param_2 + 0x34) & 0xfffffffd;
  FUN_0043dfa4(param_2,2);
  return unaff_r7;
}

