
void FUN_0058c622(int param_1,int param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int local_78;
  undefined4 local_74;
  int local_68;
  undefined4 local_58;
  int local_48;
  undefined4 uStack_18;
  
  uVar1 = DAT_0058c798;
  uStack_18 = param_4;
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_74 = DAT_0058c78c;
      local_78 = 0x11a;
      FUN_0043d574(1,DAT_0058c744,DAT_0058c740,DAT_0058c790);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058c794);
    }
  }
  else {
    FUN_00450500(param_1,DAT_0058c798);
    if (param_2 == 0) {
      param_2 = 0xfa;
    }
    FUN_004503d6(&local_78);
    local_78 = param_1;
    FUN_004506ce(&local_78,0,0xff);
    local_74 = uVar1;
    local_58 = DAT_0058c79c;
    if (param_3 != 0) {
      local_68 = param_3;
    }
    local_48 = param_2;
    FUN_00450408(&local_78);
  }
  return;
}

