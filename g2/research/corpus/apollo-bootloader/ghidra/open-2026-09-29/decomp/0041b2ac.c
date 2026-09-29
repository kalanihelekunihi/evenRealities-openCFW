
void FUN_0041b2ac(void)

{
  bool bVar1;
  char cVar2;
  undefined4 *puVar3;
  
  puVar3 = *(undefined4 **)*DAT_0041b388;
  setProcStackPointerLimit(*puVar3);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setThreadModePrivileged(1);
    bVar1 = (bool)isThreadMode();
    if (bVar1) {
      cVar2 = isUsingMainStack();
      setStackMode(cVar2 == '\x01');
    }
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(puVar3 + 10);
  }
  InstructionSynchronizationBarrier(0xf);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setBasePriority(0);
  }
                    /* WARNING: Could not recover jumptable at 0x0041b2d0. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*(code *)puVar3[1])(0,2);
  return;
}

