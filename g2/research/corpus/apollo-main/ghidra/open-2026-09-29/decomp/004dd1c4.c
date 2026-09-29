
void FUN_004dd1c4(int *param_1,char param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  int local_70;
  undefined4 local_6c;
  int local_68;
  undefined4 local_64;
  undefined4 local_60;
  int *local_54;
  undefined4 local_50;
  undefined4 local_40;
  undefined4 local_38;
  undefined4 local_34;
  
  if (((param_1 != (int *)0x0) && (*param_1 != 0)) && (param_1[1] != 0)) {
    iVar1 = FUN_0043fce0(param_1[1]);
    if (iVar1 != 0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_6c = DAT_004dd4cc;
        local_70 = 0x156;
        local_68 = iVar1;
        FUN_0043d574(2,DAT_004dd474,DAT_004dd470,DAT_004dd4d0);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_004dd4d4,DAT_004dd4d4,iVar1);
      }
      FUN_0043f142(param_1[1],0);
    }
    if (param_2 == '\0') {
      uVar3 = 0xfffffff0;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_64 = 0xfffffff0;
        local_68 = 0;
        local_6c = DAT_004dd4e0;
        local_70 = 0x164;
        FUN_0043d574(4,DAT_004dd474,DAT_004dd470,DAT_004dd4d0);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        local_70 = -0x10;
        compress_log_output(0x10800000,DAT_004dd4e4,DAT_004dd4e4,0);
      }
    }
    else {
      uVar3 = 0x10;
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        local_64 = 0x10;
        local_68 = 0;
        local_6c = DAT_004dd4d8;
        local_70 = 0x160;
        FUN_0043d574(4,DAT_004dd474,DAT_004dd470,DAT_004dd4d0);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        local_70 = 0x10;
        compress_log_output(0x10800000,DAT_004dd4dc,DAT_004dd4dc,0);
      }
    }
    FUN_004503d6(&local_70);
    local_70 = param_1[1];
    FUN_004506ce(&local_70,0,uVar3);
    local_40 = 0x96;
    local_6c = DAT_004dd4e8;
    local_50 = DAT_004dd4ec;
    local_34 = 0x96;
    local_38 = 0;
    local_60 = DAT_004dd4f0;
    local_54 = param_1;
    FUN_00450408(&local_70);
  }
  return;
}

