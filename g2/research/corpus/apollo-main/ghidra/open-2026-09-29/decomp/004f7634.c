
void FUN_004f7634(undefined1 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  int *piVar1;
  undefined1 uVar2;
  int iVar3;
  int local_78;
  undefined4 local_74;
  int local_68;
  undefined4 local_48;
  undefined4 uStack_18;
  
  piVar1 = DAT_004f8094;
  if ((*DAT_004f8094 != 0) && (uStack_18 = param_4, iVar3 = FUN_0043e2ea(*DAT_004f8094), iVar3 != 0)
     ) {
    FUN_004503d6(&local_78);
    local_78 = *piVar1;
    uVar2 = FUN_004f505c(*piVar1,0);
    FUN_004506ce(&local_78,uVar2,param_1);
    local_74 = DAT_004f8320;
    if (param_3 != 0) {
      local_68 = param_3;
    }
    local_48 = param_2;
    FUN_00450408(&local_78);
  }
  return;
}

