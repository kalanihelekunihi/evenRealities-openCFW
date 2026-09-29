
void FUN_004d43d4(void)

{
  DataMemoryBarrier(0x1f);
  *DAT_004d4608 = *DAT_004d4608 & 0xfffeffff;
  *DAT_004d4604 = *DAT_004d4604 & 0xfffffffe;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return;
}

