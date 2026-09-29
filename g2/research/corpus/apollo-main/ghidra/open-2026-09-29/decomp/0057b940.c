
undefined8 PDM0_IRQHandler(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined4 *puVar2;
  int iVar3;
  int local_18;
  undefined4 local_14;
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_18 = param_1;
  local_14 = param_2;
  local_10 = param_3;
  uStack_c = param_4;
  iVar3 = productModeGet();
  puVar2 = DAT_0057ba78;
  puVar1 = DAT_0057ba48;
  if ((iVar3 == 1) && (*DAT_0057ba74 == '\0')) {
    FUN_005925e0(*DAT_0057ba78,&local_18,1);
    FUN_005925b4(*puVar2,local_18);
    FUN_00592484(*puVar2,local_18,DAT_0057ba7c);
    if (local_18 << 0x1c < 0) {
      aud_send_codec_control_message();
    }
  }
  else {
    FUN_005925e0(*DAT_0057ba48,&local_18,1);
    FUN_005925b4(*puVar1,local_18);
    FUN_00592484(*puVar1,local_18,DAT_0057ba54);
    if (local_18 << 0x1c < 0) {
      local_10 = 0;
      local_14 = 0;
      drv_pdm_buffer_get(&local_10,&local_14);
      service_algo_energy_window_update(local_10,local_14);
    }
  }
  return CONCAT44(local_14,local_18);
}

