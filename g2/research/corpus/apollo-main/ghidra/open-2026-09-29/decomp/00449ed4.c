
void service_time_epoch_to_calendar24
               (uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  uint uVar2;
  ushort uVar3;
  undefined1 auStack_70 [4];
  uint local_6c;
  int local_64;
  int local_60;
  int local_5c;
  uint local_58;
  uint local_54;
  uint local_50;
  undefined1 auStack_48 [28];
  undefined1 auStack_2c [28];
  undefined4 uStack_10;
  
  uStack_10 = param_4;
  FUN_00439c04(auStack_2c,DAT_0044a3f0,0x1c);
  FUN_00439c04(auStack_48,DAT_0044a3f4,0x1c);
  if (param_1 < DAT_0044a3f8) {
    uVar2 = 0;
    param_1 = 0;
  }
  else {
    uVar2 = DAT_0044a400 + param_1 / DAT_0044a3fc;
    param_1 = param_1 - DAT_0044a3fc * (param_1 / DAT_0044a3fc);
  }
  local_50 = param_1 % 0x3c;
  local_54 = (param_1 / 0x3c) % 0x3c;
  local_58 = (param_1 / 0x3c) / 0x3c;
  local_6c = (uVar2 + 6) % 7;
  uVar3 = (short)(uVar2 / 0x5b5) * 4 + 2000;
  uVar2 = uVar2 % 0x5b5;
  if (uVar2 < 0x16e) {
    puVar1 = auStack_2c;
  }
  else {
    puVar1 = auStack_48;
    uVar3 = (short)((uVar2 - 1) / 0x16d) + uVar3;
    uVar2 = (uVar2 - 1) % 0x16d;
  }
  local_60 = uVar2 / 0x1f + 1;
  if (*(ushort *)(puVar1 + local_60 * 2) <= uVar2) {
    local_60 = uVar2 / 0x1f + 2;
  }
  local_5c = (uVar2 - *(ushort *)(puVar1 + local_60 * 2 + -2)) + 1;
  local_64 = uVar3 - 2000;
  FUN_00439be4(param_2,auStack_70,0x28);
  return;
}

