
void xPortSysTickHandler(void)

{
  undefined4 uVar1;
  int iVar2;
  
  uVar1 = ulSetInterruptMaskFromISR();
  iVar2 = xTaskIncrementTick();
  if (iVar2 != 0) {
    *(undefined4 *)(DAT_0800c5cc + 4) = 0x10000000;
  }
  vClearInterruptMaskFromISR(uVar1);
  return;
}

