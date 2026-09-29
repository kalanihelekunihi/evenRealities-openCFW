
void touch_platform_1238_routes(void)

{
  undefined4 uVar1;
  
  uVar1 = DAT_00004584;
  Cy_GPIO_Pin_Init(DAT_00004584,2,DAT_00004580);
  Cy_GPIO_Pin_Init(uVar1,3,DAT_00004588);
  uVar1 = DAT_00004590;
  Cy_GPIO_Pin_Init(DAT_00004590,2,DAT_0000458c);
  Cy_GPIO_Pin_Init(uVar1,3,DAT_00004594);
  uVar1 = DAT_0000459c;
  Cy_GPIO_Pin_Init(DAT_0000459c,0,DAT_00004598);
  Cy_GPIO_Pin_Init(uVar1,1,DAT_000045a0);
  return;
}

