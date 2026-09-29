
void thread_notification_destroy(void)

{
  int iVar1;
  
  iVar1 = DAT_0048e444;
  if (*(int *)(DAT_0048e444 + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_0048e444 + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  func_0x0049739e();
  return;
}

