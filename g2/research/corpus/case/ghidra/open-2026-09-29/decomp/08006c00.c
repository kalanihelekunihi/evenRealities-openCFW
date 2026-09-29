
void case_initialize_controller_profile(void)

{
  undefined4 *puVar1;
  int iVar2;
  
  puVar1 = DAT_08006c74;
  *DAT_08006c74 = DAT_08006c70;
  puVar1[1] = DAT_08006c78;
  puVar1[2] = 0;
  puVar1[3] = 0;
  puVar1[4] = 0;
  puVar1[6] = 0;
  puVar1[7] = 0;
  puVar1[8] = 0;
  puVar1[5] = 0xc;
  puVar1[9] = 0;
  puVar1[10] = 0x10;
  puVar1[0xf] = 0x1000;
  iVar2 = case_prepare_controller_context();
  if (iVar2 != 0) {
    case_fail_stop();
  }
  iVar2 = case_guarded_controller_field_high(DAT_08006c74,0);
  if (iVar2 != 0) {
    case_fail_stop();
  }
  iVar2 = case_guarded_controller_field_mid(DAT_08006c74,0);
  if (iVar2 != 0) {
    case_fail_stop();
  }
  iVar2 = case_guarded_controller_disable(DAT_08006c74);
  if (iVar2 != 0) {
    case_fail_stop();
  }
  case_start_context_transfer(DAT_08006c74,DAT_08006c7c,1);
  return;
}

