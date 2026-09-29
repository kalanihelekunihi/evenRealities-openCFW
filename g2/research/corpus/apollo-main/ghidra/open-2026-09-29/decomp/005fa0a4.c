
undefined8 ulSetInterruptMask(void)

{
  bool bVar1;
  undefined4 uVar2;
  
  uVar2 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar2 = getBasePriority();
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setBasePriority(0x30);
  }
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  return CONCAT44(0x30,uVar2);
}

