
void FUN_0058c328(int param_1,int param_2,int param_3,int param_4)

{
  undefined4 uVar1;
  int iVar2;
  int local_78;
  undefined4 local_74;
  int local_68;
  undefined4 local_58;
  int local_48;
  int local_44;
  
  uVar1 = DAT_0058c74c;
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0058c744,DAT_0058c740,DAT_0058c75c,0x9f,DAT_0058c738);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058c748);
    }
  }
  else {
    FUN_00450500(param_1,DAT_0058c74c);
    if (param_2 == 0) {
      param_2 = 0xfa;
    }
    FUN_004503d6(&local_78);
    local_78 = param_1;
    FUN_004506ce(&local_78,0,0xff);
    local_44 = -param_3;
    local_74 = uVar1;
    local_58 = DAT_0058c750;
    if (param_4 != 0) {
      local_68 = param_4;
    }
    local_48 = param_2;
    FUN_00450408(&local_78);
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_0058c744,DAT_0058c740,DAT_0058c75c,0xb1,DAT_0058c754);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_0058c758);
    }
  }
  return;
}

