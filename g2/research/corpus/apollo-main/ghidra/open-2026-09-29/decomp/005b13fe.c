
undefined8 FUN_005b13fe(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  
  iVar3 = DAT_005b15d8;
  iVar1 = FUN_005b0c18();
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_1 = 0x18b;
    param_2 = DAT_005b1aa8;
    FUN_0043d574(4,DAT_005b15d0,DAT_005b15cc,DAT_005b1aac,0x18b,DAT_005b1aa8,iVar1,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_005b1ab0,DAT_005b1ab0,iVar1);
  }
  if ((*(int *)(iVar3 + 100) != 0) &&
     (iVar2 = FUN_0043e2ea(*(undefined4 *)(iVar3 + 100)), iVar2 != 0)) {
    if (*(char *)(iVar3 + 0x96) == '\0') {
      for (; 0x14 < iVar1; iVar1 = iVar1 + -1) {
        iVar2 = FUN_0044dce2(*(undefined4 *)(iVar3 + 100),iVar1 + -1);
        if ((iVar2 != 0) && (iVar4 = FUN_0043e2ea(iVar2), iVar4 != 0)) {
          FUN_0044d7b8(iVar2);
        }
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        param_1 = 0x192;
        param_2 = DAT_005b1ab4;
        FUN_0043d574(4,DAT_005b15d0,DAT_005b15cc,DAT_005b1aac);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x10000000,PTR_s__conversate_ui_Skip_tag_delete__c_005b1ab8);
      }
    }
  }
  return CONCAT44(param_2,param_1);
}

