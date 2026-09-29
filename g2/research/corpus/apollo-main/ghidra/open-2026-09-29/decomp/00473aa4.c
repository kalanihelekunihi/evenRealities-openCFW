
void FUN_00473aa4(void)

{
  int iVar1;
  
  iVar1 = DAT_00474480;
  if (*(int *)(DAT_00474480 + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_00474480 + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

