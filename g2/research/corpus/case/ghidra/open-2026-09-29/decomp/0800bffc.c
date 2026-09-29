
void FUN_0800bffc(void)

{
  disableIRQinterrupts();
  *DAT_0800c010 = *DAT_0800c010 + 1;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return;
}

