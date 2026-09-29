
void FUN_0041fe28(void)

{
  char *pcVar1;
  
  pcVar1 = DAT_00420878;
  if (*DAT_00420878 != '\x01') {
    am_hal_mspi_power_control(*DAT_00420874,2,1);
    *pcVar1 = '\x01';
  }
  return;
}

