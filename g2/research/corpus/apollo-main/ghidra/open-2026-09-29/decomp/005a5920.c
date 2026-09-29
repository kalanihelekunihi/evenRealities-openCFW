
undefined4 atBrightnessHandler(void)

{
  undefined4 uVar1;
  
  uVar1 = thunk_FUN_0048d86c();
  settings_set_brightness_level(uVar1);
  at_core_output(PTR_s_AT_BRIGHTNESS_OK_brightness__d_005a5978,uVar1);
  return 1;
}

