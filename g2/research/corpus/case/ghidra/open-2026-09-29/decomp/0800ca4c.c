
undefined4 xTaskGetSchedulerState(void)

{
  if (*(int *)(DAT_0800ca68 + 0x14) == 0) {
    return 1;
  }
  if (*(int *)(DAT_0800ca68 + 0x30) != 0) {
    return 0;
  }
  return 2;
}

