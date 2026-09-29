
undefined4 FUN_0041b3e4(void)

{
  undefined4 unaff_r7;
  
  FUN_0041b2f8();
  *DAT_0041b524 = *DAT_0041b524 + 1;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return unaff_r7;
}

