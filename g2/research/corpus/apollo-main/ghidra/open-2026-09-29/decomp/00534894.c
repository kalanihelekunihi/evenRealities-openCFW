
void dmSecLescMsgHandler(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 *puVar1;
  undefined1 auStack_30 [2];
  undefined1 uStack_2e;
  undefined1 uStack_2d;
  undefined1 auStack_2c [16];
  undefined1 auStack_1c [16];
  undefined4 uStack_c;
  
  uStack_c = param_4;
  if (*(char *)(param_1 + 2) == 'A') {
    *(undefined1 *)(param_1 + 2) = 0x34;
    (**(code **)(DAT_00534974 + 8))(param_1);
  }
  else if (*(char *)(param_1 + 2) == '@') {
    WsfBufFree(*(undefined4 *)(param_1 + 8));
    uStack_2e = 0x33;
    uStack_2d = 0;
    FUN_00542a44(auStack_2c,*(undefined4 *)(param_1 + 4));
    puVar1 = DAT_00534978;
    FUN_00542a44(auStack_1c,*DAT_00534978);
    WsfBufFree(*puVar1);
    (**(code **)(DAT_00534974 + 8))(auStack_30);
  }
  return;
}

