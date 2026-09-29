
void FUN_00550708(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int local_78;
  int local_74;
  int local_70;
  int local_6c;
  int local_68;
  undefined4 local_58;
  undefined4 local_48;
  undefined4 uStack_18;
  
  iVar1 = DAT_00550ff4;
  if (*(int *)(DAT_00550ff4 + 0x3c) != 0) {
    uStack_18 = param_4;
    FUN_0043f66c(*(undefined4 *)(DAT_00550ff4 + 0x3c));
    piVar2 = DAT_0055100c;
    iVar3 = FUN_0043fce0(*(undefined4 *)(iVar1 + 0x3c));
    *piVar2 = iVar3;
    if ((param_1 == 1) && (iVar3 = FUN_005511bc(0), iVar3 <= *DAT_00550f7c)) {
      iVar3 = *piVar2 - *DAT_00550ebc;
    }
    else {
      if (param_1 != -1) {
        return;
      }
      if (0 < *DAT_00550f7c) {
        return;
      }
      iVar3 = *DAT_00550ebc + *piVar2;
    }
    *DAT_00550d38 = 2;
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_6c = *piVar2;
      local_74 = DAT_00551234;
      local_78 = 0x340;
      local_70 = param_1;
      local_68 = iVar3;
      FUN_0043d574(3,DAT_00550958,DAT_00550954,DAT_00551238);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      local_78 = *piVar2;
      local_74 = iVar3;
      compress_log_output(0xcc00000,DAT_0055123c,DAT_0055123c,param_1);
    }
    FUN_004503d6(&local_78);
    local_78 = *(int *)(iVar1 + 0x3c);
    FUN_004506ce(&local_78,*piVar2,iVar3);
    local_48 = *DAT_00550ff0;
    local_74 = DAT_00551010;
    local_58 = DAT_005512a8;
    local_68 = DAT_005512ac;
    FUN_00450408(&local_78);
  }
  return;
}

