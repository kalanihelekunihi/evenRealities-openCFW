
void case_initialize_controller_profile(void)

{
  undefined4 *puVar1;
  int iVar2;
  
  case_reset_controller_context(DAT_08006d64);
  puVar1 = DAT_08006d64;
  *DAT_08006d64 = DAT_08006d68;
  puVar1[1] = DAT_08006d6c;
  puVar1[2] = 0;
  puVar1[3] = 0;
  puVar1[4] = 0;
  puVar1[6] = 0;
  puVar1[7] = 0;
  puVar1[8] = 0;
  puVar1[5] = 8;
  puVar1[9] = 0;
  puVar1[10] = 0x10;
  puVar1[0xf] = 0x1000;
  iVar2 = case_prepare_controller_context();
  if (iVar2 != 0) {
    case_fail_stop();
  }
  iVar2 = case_guarded_controller_field_high(DAT_08006d64,0);
  if (iVar2 != 0) {
    case_fail_stop();
  }
  iVar2 = case_guarded_controller_field_mid(DAT_08006d64,0);
  if (iVar2 != 0) {
    case_fail_stop();
  }
  iVar2 = case_guarded_controller_disable(DAT_08006d64);
  if (iVar2 != 0) {
    case_fail_stop();
  }
  return;
}

