
void touch_platform_0338_install(undefined4 param_1)

{
  *DAT_00003650 = param_1;
  Cy_SysTick_Init(0,0x28);
  Cy_SysTick_SetCallback(0,DAT_00003654);
  return;
}

