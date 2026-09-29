
void settings_send_config_to_peer(void)

{
  int iVar1;
  undefined4 in_r3;
  undefined1 auStack_3c [4];
  undefined1 auStack_38 [28];
  undefined4 uStack_1c;
  undefined1 auStack_18 [12];
  undefined4 uStack_c;
  
  uStack_c = in_r3;
  FUN_0043c0e4(auStack_3c,0x30,0);
  iVar1 = FUN_0045a568();
  if (iVar1 == 1) {
    auStack_3c[0] = 0;
  }
  else {
    auStack_3c[0] = 1;
    FUN_0044b5a0(auStack_18,DAT_0046c400,9);
  }
  iVar1 = DAT_0046bee8;
  FUN_00439c04(auStack_38,DAT_0046bee8,0x1c);
  uStack_1c = *(undefined4 *)(iVar1 + 0x1c);
  FUN_00465480(9,auStack_3c,0x30,0,5);
  return;
}

