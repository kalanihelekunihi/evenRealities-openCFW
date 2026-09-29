
undefined4 conversate_calculate_auto_duration_by_label(undefined4 param_1,undefined4 param_2)

{
  undefined *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined4 uVar4;
  
  if ((*(int *)(DAT_005b6958 + 0x1c) == 0) || (*(char *)(DAT_005b6958 + 0x96) != '\0')) {
    uVar2 = 0xffffffff;
  }
  else {
    uVar2 = FUN_0044dce2(*(undefined4 *)(DAT_005b6958 + 0x1c),0);
    iVar3 = FUN_0043e2ea(uVar2);
    if (iVar3 == 0) {
      uVar2 = 0xffffffff;
    }
    else {
      uVar2 = FUN_0044dce2(uVar2,2);
      iVar3 = FUN_0043e2ea(uVar2);
      puVar1 = PTR_s_ID_CONVERSATE_CLOSE_IN_X_SEC_005b6970;
      if (iVar3 == 0) {
        uVar2 = 0xffffffff;
      }
      else {
        uVar4 = FUN_00460084(PTR_s_ID_CONVERSATE_CLOSE_IN_X_SEC_005b6970);
        uVar4 = FUN_0045fffe(puVar1,uVar4);
        FUN_0049954c(uVar2,uVar4,param_2);
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}

