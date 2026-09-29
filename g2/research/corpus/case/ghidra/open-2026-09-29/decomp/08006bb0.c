
void case_initialize_channel_profile(void)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = DAT_08006bfc;
  *DAT_08006bfc = DAT_08006bf8;
  puVar1[3] = 0x7f;
  puVar1[2] = 0;
  puVar1[5] = 0;
  puVar1[6] = 0;
  puVar1[4] = 0x1f;
  puVar1[7] = 0;
  puVar1[8] = 0x40000000;
  puVar1[9] = 0;
  iVar2 = case_activate_controller();
  if (iVar2 != 0) {
    case_fail_stop();
  }
  iVar2 = stm32_hal_peripheral_init(DAT_08006bfc,0xf0,4);
  if (iVar2 != 0) {
    case_fail_stop();
  }
  case_start_controller(DAT_08006bfc);
  return;
}

