
void vPortStartFirstTask(void)

{
  bool bVar1;
  char cVar2;
  undefined4 in_stack_00000000;
  undefined4 in_stack_00000004;
  code *UNRECOVERED_JUMPTABLE;
  undefined4 in_stack_0000001c;
  
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setProcessStackPointer(*(int *)*DAT_080000f0 + 0x20);
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    setThreadModePrivileged(1);
    bVar1 = (bool)isThreadMode();
    if (bVar1) {
      cVar2 = isUsingMainStack();
      setStackMode(cVar2 == '\x01');
    }
  }
  InstructionSynchronizationBarrier(0xf);
  enableIRQinterrupts();
                    /* WARNING: Could not recover jumptable at 0x080000ec. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  (*UNRECOVERED_JUMPTABLE)(in_stack_00000000,in_stack_00000004,in_stack_0000001c);
  return;
}

