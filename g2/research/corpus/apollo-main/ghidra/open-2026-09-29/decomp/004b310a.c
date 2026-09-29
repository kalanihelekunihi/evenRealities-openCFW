
void dmAdvGenConnCmpl(byte param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 auStack_38 [2];
  undefined1 uStack_36;
  undefined1 uStack_35;
  undefined1 uStack_34;
  undefined1 uStack_30;
  undefined1 uStack_2f;
  undefined1 auStack_2e [26];
  undefined4 uStack_14;
  
  uStack_14 = param_4;
  FUN_0043c0e4(auStack_38,0x24,0);
  uStack_36 = 2;
  uStack_30 = 1;
  uStack_2f = *(undefined1 *)((uint)param_1 + DAT_004b32cc + 0x31);
  uStack_35 = param_2;
  uStack_34 = param_2;
  FUN_004d293c(auStack_2e,DAT_004b32cc + (uint)param_1 * 6 + 0x25);
  dmDevPassHciEvtToConn(auStack_38);
  return;
}

