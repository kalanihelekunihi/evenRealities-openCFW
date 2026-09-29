
undefined8 als_function_34(void)

{
  undefined4 uVar1;
  uint uVar2;
  int iVar3;
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  
  uVar2 = *DAT_004ae99c;
  if (uVar2 == 1) {
    als_function_31();
    goto LAB_004ae730;
  }
  if (uVar2 != 0) {
    if (uVar2 == 3) {
      als_function_33();
      goto LAB_004ae730;
    }
    if (uVar2 < 3) {
      als_function_32();
      goto LAB_004ae730;
    }
  }
  iVar3 = FUN_0043d0ce();
  uVar1 = DAT_004aea00;
  if (iVar3 << 0x1e < 0) {
    unaff_r5 = 0x264;
    FUN_0043d574(2,DAT_004ae9e0,DAT_004ae9dc,DAT_004aea04);
    unaff_r6 = uVar1;
  }
  iVar3 = FUN_0043d0ce();
  if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
    compress_log_output(0x8000000,PTR_s__sensor_als_ALS_process_status_e_004aea08,
                        PTR_s__sensor_als_ALS_process_status_e_004aea08);
  }
LAB_004ae730:
  return CONCAT44(unaff_r6,unaff_r5);
}

