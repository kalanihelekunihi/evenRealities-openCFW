
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 process_stack_init_43293c(void)

{
  bool bVar1;
  int unaff_r5;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  uStack_4 = uRam00432954;
  uStack_8 = uRam00432954;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(&uStack_8);
  }
  fpu_enable_432958(&uStack_8);
  runtime_start_43297c();
  VectorStoreRegister(unaff_r5 + -0x3d4,1,2,0);
  _DAT_e000ed88 = _DAT_e000ed88 | 0xf00000;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return 0x2040000;
}

