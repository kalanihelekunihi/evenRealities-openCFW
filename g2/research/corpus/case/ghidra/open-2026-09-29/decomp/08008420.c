
void systick_gate(void)

{
  int iVar1;
  
  iVar1 = xTaskGetSchedulerState(*(undefined4 *)(DAT_08008434 + 0x10));
  if (iVar1 != 1) {
    xPortSysTickHandler();
  }
  return;
}

