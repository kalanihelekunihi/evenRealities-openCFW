
void osKernelGetTickCount(void)

{
  int iVar1;
  
  iVar1 = IRQ_Context();
  if (iVar1 == 0) {
    xTaskGetTickCount();
  }
  else {
    xTaskGetTickCountFromISR();
  }
  return;
}

