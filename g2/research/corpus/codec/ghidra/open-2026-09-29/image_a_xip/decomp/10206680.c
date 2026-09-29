
undefined4 gx8002_rtc_isr(undefined4 param_1)

{
  undefined4 uVar1;
  
  if (*DAT_10206698 == 0) {
    uVar1 = 0;
  }
  else {
    uVar1 = (*(code *)(*DAT_10206698 & 0xfffffffe))(param_1,DAT_10206698[1]);
  }
  return uVar1;
}

