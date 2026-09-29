
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_004abfba(void)

{
  undefined *puVar1;
  int iVar2;
  undefined4 unaff_r5;
  undefined *unaff_r6;
  
  if (*DAT_004acb00 != '\0') {
    iVar2 = FUN_0043d0ce();
    puVar1 = PTR_s_clear_force_out_box_flag_on_real_004ac820;
    if (iVar2 << 0x1e < 0) {
      unaff_r5 = 0x99;
      FUN_0043d574(3,PTR_s_box_detect_004ac81c,DAT_004ac818,
                   PTR_s__BoxDetect_ClearForceOutBoxOnRea_004ac824);
      unaff_r6 = puVar1;
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,_DAT_004acb04,_DAT_004acb04);
    }
    FUN_004ac5a2(0);
    FUN_004ac672(0);
  }
  return CONCAT44(unaff_r6,unaff_r5);
}

