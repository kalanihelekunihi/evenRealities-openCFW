
undefined4 FUN_004c9104(int param_1,undefined4 param_2,undefined1 *param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  char local_120 [8];
  undefined1 auStack_118 [256];
  int iStack_18;
  
  if (param_4 == 0) {
    uVar1 = 0xb;
  }
  else {
    uVar1 = *(undefined4 *)(param_1 + 0x30);
    *param_3 = 0;
    iStack_18 = param_4;
    do {
      iVar2 = FUN_004cfd02(uVar1,param_2,local_120);
      if (iVar2 < 0) {
        return 0xc;
      }
      if (iVar2 == 0) {
        *param_3 = 0;
        break;
      }
      if (local_120[0] == '\x02') {
        snprintf(param_3,param_4,&DAT_004c917c,auStack_118);
      }
      else {
        FUN_00454778(param_3,auStack_118,param_4);
      }
      iVar2 = FUN_004547be(param_3,&DAT_004c9180);
    } while ((iVar2 == 0) || (iVar2 = FUN_004547be(param_3,&DAT_004c9184), iVar2 == 0));
    uVar1 = 0;
  }
  return uVar1;
}

