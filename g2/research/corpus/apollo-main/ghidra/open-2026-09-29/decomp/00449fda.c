
void service_time_epoch_to_calendar_configured(uint param_1,undefined4 param_2)

{
  undefined1 *puVar1;
  int iVar2;
  ushort uVar3;
  uint uVar4;
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
  
  FUN_00439c04(auStack_2c,DAT_0044a404,0x1c);
  FUN_00439c04(auStack_48,DAT_0044a408,0x1c);
  if (param_1 < DAT_0044a3f8) {
    uVar4 = 0;
    param_1 = 0;
  }
  else {
    uVar4 = DAT_0044a400 + param_1 / DAT_0044a3fc;
    param_1 = param_1 - DAT_0044a3fc * (param_1 / DAT_0044a3fc);
  }
  local_50 = param_1 % 0x3c;
  local_54 = (param_1 / 0x3c) % 0x3c;
  local_58 = (param_1 / 0x3c) / 0x3c;
  iVar2 = FUN_0046650c();
  if ((iVar2 == 1) && (local_58 = local_58 % 0xc, local_58 == 0)) {
    local_58 = 0xc;
  }
  local_6c = (uVar4 + 6) % 7;
  uVar3 = (short)(uVar4 / 0x5b5) * 4 + 2000;
  uVar4 = uVar4 % 0x5b5;
  if (uVar4 < 0x16e) {
    puVar1 = auStack_2c;
  }
  else {
    puVar1 = auStack_48;
    uVar3 = (short)((uVar4 - 1) / 0x16d) + uVar3;
    uVar4 = (uVar4 - 1) % 0x16d;
  }
  local_60 = uVar4 / 0x1f + 1;
  if (*(ushort *)(puVar1 + local_60 * 2) <= uVar4) {
    local_60 = uVar4 / 0x1f + 2;
  }
  local_5c = (uVar4 - *(ushort *)(puVar1 + local_60 * 2 + -2)) + 1;
  local_64 = uVar3 - 2000;
  FUN_00439be4(param_2,auStack_70,0x28);
  return;
}

