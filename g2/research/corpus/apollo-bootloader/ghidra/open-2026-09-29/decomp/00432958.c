
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 fpu_enable_432958(void)

{
  _DAT_e000ed88 = _DAT_e000ed88 | 0xf00000;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return 0x2040000;
}

