
void device_mgr_fn_004c6990(void)

{
  char *pcVar1;
  int iVar2;
  
  pcVar1 = (char *)FUN_0050938e(0);
  if ((*(int *)(DAT_004c6ca0 + 4) < 1) && (-1 < *(int *)(DAT_004c6ca0 + 0xc))) {
    iVar2 = FUN_00443484();
    if (iVar2 == 1) {
      iVar2 = FUN_0044349c();
      if (iVar2 == 1) {
        FUN_00464c36(0,0,0,0);
        osDelay(500);
      }
      iVar2 = FUN_004434b4();
      if (iVar2 == 1) {
        FUN_00464c36(0,0,0,0);
        osDelay(500);
      }
    }
    if (*pcVar1 == '\x01') {
      FUN_00512a70();
    }
  }
  return;
}

