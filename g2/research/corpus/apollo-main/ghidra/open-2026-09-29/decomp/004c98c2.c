
void FUN_004c98c2(void)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  
  iVar3 = 0;
  FUN_004c94c8();
  FUN_004c9508();
  FUN_004c951c();
  FUN_004c963a();
  *DAT_004c9cd4 = 1;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    FUN_0043d574(3,DAT_004c9ca4,DAT_004c9ca0,PTR_s__thread_manager_004c9ce0,0x123,
                 PTR_s_software_version__V_s_004c9cdc,PTR_s_2_2_6_10_004c9cd8);
  }
  iVar1 = FUN_0043d0ce();
  if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
    compress_log_output(0xc400000,PTR_s__task_manager_software_version__V_004c9ce4,
                        PTR_s__task_manager_software_version__V_004c9ce4,PTR_s_2_2_6_10_004c9cd8);
  }
  do {
    while( true ) {
      uVar2 = osThreadFlagsWait(0xffffff,0,60000);
      iVar1 = osKernelGetTickCount();
      if ((uVar2 == 0) || (0x7fffffff < uVar2)) break;
      FUN_004c995e(uVar2);
    }
    if (59999 < (uint)(iVar1 - iVar3)) {
      iVar3 = iVar1;
    }
  } while( true );
}

