
void Cy_Flash_ClockBackup(void)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar1 = DAT_00008cf4;
  local_10 = DAT_00008cec;
  local_c = DAT_00008cf0;
  *(undefined4 **)(DAT_00008cf4 + 8) = &local_10;
  *(undefined4 *)(iVar1 + 4) = DAT_00008cf8;
  ProcessStatusCode();
  *(undefined4 *)(DAT_00008cfc + 0x30) = 0x80000000;
  return;
}

