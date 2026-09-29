
void case_register_pair_commit
               (undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  *(uint *)(DAT_08003f34 + 0x14) = *(uint *)(DAT_08003f34 + 0x14) | 1;
  *param_1 = param_3;
  InstructionSynchronizationBarrier(0xf);
  param_1[1] = param_4;
  return;
}

