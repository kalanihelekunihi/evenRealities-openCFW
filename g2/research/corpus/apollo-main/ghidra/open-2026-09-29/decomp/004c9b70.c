
void FUN_004c9b70(void)

{
  int iVar1;
  
  iVar1 = DAT_004c9c58;
  if (*(int *)(DAT_004c9c58 + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_004c9c58 + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

