
void FUN_0058c516(int param_1,int param_2,int param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  int local_80;
  undefined4 local_7c;
  int local_70;
  undefined4 local_60;
  int local_50;
  int local_4c;
  int iStack_20;
  
  uVar1 = DAT_0058c74c;
  iStack_20 = param_4;
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058c744,DAT_0058c740,DAT_0058c77c,0xd1,DAT_0058c778);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058c780,DAT_0058c780);
    }
  }
  else {
    FUN_00450500(param_1,DAT_0058c74c);
    local_50 = param_2;
    if (param_2 == 0) {
      local_50 = 0xfa;
    }
    FUN_004503d6(&local_80);
    local_80 = param_1;
    FUN_004506ce(&local_80,0xff,0);
    local_4c = -param_3;
    local_7c = uVar1;
    local_60 = DAT_0058c76c;
    if (param_4 != 0) {
      local_70 = param_4;
    }
    FUN_00450408(&local_80);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0058c744,DAT_0058c740,DAT_0058c77c,0xe2,DAT_0058c784,param_3,param_2);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_0058c788,DAT_0058c788,param_3,param_2);
    }
  }
  return;
}

