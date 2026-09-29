
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_005e4254(void)

{
  bool bVar1;
  int unaff_r5;
  undefined4 uStack_8;
  undefined4 uStack_4;
  
  uStack_4 = uRam005e426c;
  uStack_8 = uRam005e426c;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(&uStack_8);
  }
  FUN_005e4270(&uStack_8);
  FUN_005e4294();
  VectorStoreRegister(unaff_r5 + -0x3d4,1,2,0);
  _DAT_e000ed88 = _DAT_e000ed88 | 0xf00000;
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return 0x2040000;
}

