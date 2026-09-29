
int pvTaskIncrementMutexHeldCount(void)

{
  int *piVar1;
  
  piVar1 = DAT_0045605c;
  if (*DAT_0045605c != 0) {
    *(int *)(*DAT_0045605c + 100) = *(int *)(*DAT_0045605c + 100) + 1;
  }
  return *piVar1;
}

