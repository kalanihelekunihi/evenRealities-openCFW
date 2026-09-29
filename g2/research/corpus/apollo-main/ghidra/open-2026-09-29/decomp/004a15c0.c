
undefined8
APP_MasterClearRingConnectFailureNotifyAfterRetry
          (undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  char *pcVar1;
  int iVar2;
  
  pcVar1 = DAT_004a1fac;
  if ((*DAT_004a1fac != '\0') || (*DAT_004a1fb0 != 0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = (uint)*DAT_004a1fb0;
      param_1 = 0x37a;
      param_2 = DAT_004a204c;
      FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a2050,0x37a,DAT_004a204c,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004a2054,DAT_004a2054,*DAT_004a1fb0,param_1,param_2,param_3)
      ;
    }
  }
  *pcVar1 = '\0';
  *DAT_004a1fb0 = 0;
  return CONCAT44(param_2,param_1);
}

