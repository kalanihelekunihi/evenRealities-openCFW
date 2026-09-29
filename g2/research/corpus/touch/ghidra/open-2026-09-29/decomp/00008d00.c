
void Cy_Flash_ClockConfig(void)

{
  int iVar1;
  
  iVar1 = DAT_00008d14;
  *(undefined4 *)(DAT_00008d14 + 8) = DAT_00008d18;
  *(undefined4 *)(iVar1 + 4) = DAT_00008d1c;
  ProcessStatusCode();
  return;
}

