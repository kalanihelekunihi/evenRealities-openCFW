
undefined8 vStartFirstTask(void)

{
  bool bVar1;
  undefined4 uVar2;
  
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setMainStackPointer(*(undefined4 *)*DAT_005fa138);
  }
  enableIRQinterrupts();
  enableFIQinterrupts();
  DataSynchronizationBarrier(0xf);
  InstructionSynchronizationBarrier(0xf);
  software_interrupt(2);
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

