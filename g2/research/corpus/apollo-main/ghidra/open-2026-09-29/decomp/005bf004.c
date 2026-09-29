
undefined4
FUN_005bf004(int param_1,int param_2,undefined4 *param_3,undefined4 param_4,undefined4 param_5)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 local_48;
  undefined4 local_44;
  int local_3c;
  undefined4 local_38;
  undefined4 local_34;
  undefined4 local_28;
  undefined4 local_24;
  int local_20;
  undefined4 uStack_10;
  
  if (((param_1 == 0) || (param_3 == (undefined4 *)0x0)) || (param_2 == 0)) {
    uVar1 = 6;
  }
  else {
    local_44 = param_5;
    local_38 = *param_3;
    local_28 = DAT_005bf0ac;
    local_24 = DAT_005bf0b0;
    local_48 = param_4;
    local_3c = param_2;
    local_20 = param_1;
    uStack_10 = param_4;
    iVar2 = FUN_005beac2(&local_48,0xf,DAT_005bf094,0x38);
    if (iVar2 == 0) {
      iVar2 = FUN_005beb90(&local_48,4);
      if (iVar2 == 1) {
        *param_3 = local_34;
        iVar2 = FUN_005bea86(&local_48);
      }
      else {
        FUN_005bea86(&local_48);
        if (iVar2 == 0) {
          iVar2 = -5;
        }
      }
      if (iVar2 == -4) {
        uVar1 = 0x40;
      }
      else if (iVar2 == -5) {
        uVar1 = 10;
      }
      else if (iVar2 == -3) {
        uVar1 = 8;
      }
      else {
        uVar1 = 0;
      }
    }
    else {
      uVar1 = 6;
    }
  }
  return uVar1;
}

