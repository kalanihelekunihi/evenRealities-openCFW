
uint onboarding_flag_update(uint param_1)

{
  byte bVar1;
  byte *pbVar2;
  uint local_8;
  
  local_8 = param_1;
  pbVar2 = (byte *)kvdbOnboardingConfigPointer(0);
  if (pbVar2 == (byte *)0x0) {
    bVar1 = 0;
  }
  else {
    bVar1 = *pbVar2;
  }
  if ((uint)bVar1 != (local_8 & 0xff)) {
    SVC_SetKvdbOnboardingConfig(0,&local_8);
    *DAT_0047e634 = 1;
    osEventFlagsSet(*DAT_0047e64c,4);
  }
  return local_8;
}

