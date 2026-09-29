
void Cy_SysTick_Enable(void)

{
  uint *puVar1;
  
  puVar1 = DAT_0000a634;
  *DAT_0000a634 = *DAT_0000a634 | 2;
  *puVar1 = *puVar1 | 1;
  return;
}

