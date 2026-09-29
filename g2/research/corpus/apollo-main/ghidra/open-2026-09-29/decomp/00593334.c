
/* WARNING: Type propagation algorithm not settling */

undefined4
jbd4010_set_current_6bit(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint auStack_28 [6];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  FUN_0043c0e4(auStack_28 + 1,0x14,0);
  jbd4010_write_command(6,auStack_28 + 1,0);
  jbd4010_write_command(0xa9,auStack_28 + 1,0);
  auStack_28[0] = param_1 & 0x3f;
  jbd4010_write_command(0x46,auStack_28,1);
  auStack_28[1] = 4;
  jbd4010_write_command(0x31,auStack_28 + 1,1);
  jbd4010_write_command(0xa3,auStack_28 + 1,0);
  jbd4010_write_command(0x97,auStack_28 + 1,0);
  FUN_004910f4(1);
  return 0;
}

