
void threadBleProductionDeinit(void)

{
  int iVar1;
  
  iVar1 = DAT_00538b5c;
  if (*(int *)(DAT_00538b5c + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_00538b5c + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

