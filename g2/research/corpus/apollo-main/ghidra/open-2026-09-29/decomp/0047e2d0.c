
undefined4 onboarding_common_data_handler(byte param_1,char *param_2)

{
  char *pcVar1;
  undefined4 *puVar2;
  
  pcVar1 = DAT_0047e60c;
  DAT_0047e60c[2] = '\0';
  puVar2 = DAT_0047e610;
  if (param_1 == 1) {
    osMutexAcquire(*DAT_0047e610,0xffffffff);
    if (*pcVar1 != *param_2) {
      pcVar1[1] = '\0';
    }
    *pcVar1 = *param_2;
    pcVar1[2] = '\x02';
    osMutexRelease(*puVar2);
  }
  else if ((param_1 == 0) || ((param_1 != 3 && (2 < param_1)))) {
    return 1;
  }
  return 0;
}

