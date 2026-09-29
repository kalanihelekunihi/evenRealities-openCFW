
void jbd4010_standby_mode(void)

{
  undefined4 in_r3;
  undefined1 auStack_20 [20];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_0043c0e4(auStack_20,0x14,0);
  jbd4010_write_command(0x71,auStack_20,0);
  FUN_00491102(2);
  jbd4010_write_command(0x73,auStack_20,0);
  FUN_00491102(2);
  jbd4010_write_command(0x97,auStack_20,0);
  osDelay(2);
  return;
}

