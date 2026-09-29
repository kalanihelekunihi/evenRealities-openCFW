
undefined8 FUN_00448e48(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  iVar2 = FUN_00448e2a();
  if (iVar2 != 0) {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_Crash_info_recovered_from_previo_00448fdc;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x3fa;
      FUN_0043d574(2,PTR_s_elog_async_00448fe8,PTR_s_D__01_workspace_s200_ap510b_iar__00448fe4,
                   PTR_s_elog_async_ext_flieStore_Init_00448fe0);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__elog_async_Crash_info_recovered_00448fec,
                          PTR_s__elog_async_Crash_info_recovered_00448fec);
    }
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

