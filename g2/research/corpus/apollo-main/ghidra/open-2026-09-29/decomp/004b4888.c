
void FUN_004b4888(void)

{
  undefined1 *puVar1;
  
  FUN_004733ee(DAT_004b4d68);
  puVar1 = DAT_004b4d6c;
  *DAT_004b4d6c = 1;
  HciDrvRadioBoot(0);
  *puVar1 = 0;
  return;
}

