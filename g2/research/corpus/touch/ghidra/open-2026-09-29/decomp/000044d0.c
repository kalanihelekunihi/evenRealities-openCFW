
void touch_startup_11d0_configure_dividers(void)

{
  Cy_SysClk_PeriphDisableDivider(1,1);
  Cy_SysClk_PeriphSetDivider(1,1,3);
  Cy_SysClk_PeriphEnableDivider(1,1);
  Cy_SysClk_PeriphDisableDivider(2,0);
  Cy_SysClk_PeriphSetFracDivider(2,0,0x33,3);
  Cy_SysClk_PeriphEnableDivider(2,0);
  Cy_SysClk_PeriphDisableDivider(3,0);
  Cy_SysClk_PeriphSetFracDivider(3,0,0x33,3);
  Cy_SysClk_PeriphEnableDivider(3,0);
  return;
}

