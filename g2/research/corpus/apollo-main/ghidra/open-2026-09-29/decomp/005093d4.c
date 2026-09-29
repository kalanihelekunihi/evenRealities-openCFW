
undefined4 FUN_005093d4(void)

{
  char *pcVar1;
  int iVar2;
  
  pcVar1 = (char *)FUN_0050938e(3);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(2,0x509468,PTR_s_D__01_workspace_s200_ap510b_iar__005094b8,
                 PTR_s_power_init_005094b4,0x18e,PTR_s_hw_version___d__hw_adc_val___d_005094b0,
                 pcVar1[1],*(undefined2 *)(pcVar1 + 2));
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x8800000,PTR_s__BSP_hw_version___d__hw_adc_val__005094bc,
                        PTR_s__BSP_hw_version___d__hw_adc_val__005094bc,pcVar1[1],
                        *(undefined2 *)(pcVar1 + 2));
  }
  if (*pcVar1 == '\x01') {
    FUN_00512644();
  }
  else if (*pcVar1 == '\x02') {
    DRV_Bq25180HwInit();
    DRV_Bq27427HwInit();
  }
  return 0;
}

