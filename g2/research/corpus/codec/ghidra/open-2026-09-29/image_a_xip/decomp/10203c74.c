
void gx_analog_config_update_enable(void)

{
  int iVar1;
  
  iVar1 = iRam10203c84;
  *(undefined4 *)(iRam10203c84 + 0x40) = 0x59;
  *(undefined4 *)(iVar1 + 0x44) = 0x59;
  *(undefined4 *)(iVar1 + 0x48) = 0x59;
  *(undefined4 *)(iVar1 + 0x4c) = 0x59;
  return;
}

