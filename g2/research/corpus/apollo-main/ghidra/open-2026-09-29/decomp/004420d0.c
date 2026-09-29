
undefined4 FUN_004420d0(void)

{
  undefined4 unaff_r7;
  
  ulSetInterruptMask();
  *DAT_00442210 = *DAT_00442210 + 1;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return unaff_r7;
}

