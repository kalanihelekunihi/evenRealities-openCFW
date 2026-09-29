
void gx8002_bunkws_offset_clear(void)

{
  int iVar1;
  
  iVar1 = iRam10208b74;
  *(undefined4 *)(iRam10208b74 + 0xc) = 0;
  *(undefined4 *)(iVar1 + 4) = 0;
  return;
}

