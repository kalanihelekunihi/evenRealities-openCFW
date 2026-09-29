
void case_initialize_application_profile(void)

{
  int iVar1;
  undefined4 local_58 [3];
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_30;
  undefined4 local_2c;
  undefined4 local_28;
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 local_18;
  undefined4 local_14;
  
  FUN_080001e6(local_58,0x38);
  local_20 = 0;
  local_1c = 0;
  local_18 = 0;
  local_14 = 0;
  case_configure_mode_wait(0x200);
  local_58[0] = 10;
  local_4c = 0x100;
  local_44 = 0x40;
  local_40 = 1;
  local_30 = 8;
  local_2c = 0x20000;
  local_3c = 2;
  local_28 = 0x2000000;
  local_38 = 2;
  local_48 = 0;
  local_24 = 0x20000000;
  local_34 = 0;
  iVar1 = case_configure_system_clock(local_58);
  if (iVar1 != 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  local_20 = 7;
  local_18 = 0;
  local_1c = 2;
  local_14 = 0;
  iVar1 = case_configure_clock_path(&local_20,2);
  if (iVar1 != 0) {
    disableIRQinterrupts();
    do {
                    /* WARNING: Do nothing block with infinite loop */
    } while( true );
  }
  return;
}

