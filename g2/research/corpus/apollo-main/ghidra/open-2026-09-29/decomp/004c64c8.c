
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void device_mgr_fn_004c64c8(void)

{
  int iVar1;
  
  device_mgr_fn_004c632c();
  device_mgr_fn_004c6498();
  do {
    iVar1 = osMessageQueueGet(*(undefined4 *)(DAT_004c6c08 + 0xc),&stack0xfffffff0,0,0xffffffff);
    if (iVar1 == 0) {
      device_mgr_fn_004c6510(&stack0xfffffff0);
    }
    else {
      *_DAT_004c6c50 = *_DAT_004c6c50 + 1;
    }
    osDelay(1);
  } while( true );
}

