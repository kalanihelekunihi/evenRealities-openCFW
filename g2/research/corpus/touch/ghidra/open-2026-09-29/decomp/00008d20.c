
void Cy_Flash_ClockRestore(void)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  iVar1 = DAT_00008d48;
  local_10 = DAT_00008d40;
  local_c = DAT_00008d44;
  *(undefined4 **)(DAT_00008d48 + 8) = &local_10;
  *(undefined4 *)(iVar1 + 4) = DAT_00008d4c;
  ProcessStatusCode();
  return;
}

