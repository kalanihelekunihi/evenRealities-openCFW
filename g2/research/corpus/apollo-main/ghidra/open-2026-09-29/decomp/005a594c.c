
undefined8 atBrightnessReadHandler(void)

{
  undefined4 uVar1;
  undefined4 unaff_r7;
  
  uVar1 = service_settings_auto_brightness();
  at_core_output(PTR_s_AT_BRIGHTNESS_READ_OK_brightness_005a5980,uVar1);
  return CONCAT44(unaff_r7,1);
}

