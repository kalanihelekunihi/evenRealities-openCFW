
undefined8 tracepoint_insert_file_sorted(uint param_1,uint param_2,uint param_3,uint param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 *puVar5;
  uint uVar6;
  uint uVar7;
  
  iVar1 = DAT_005ee794;
  uVar6 = param_1;
  uVar7 = param_2;
  if (*(uint *)(DAT_005ee794 + 0x80) < 0x10) {
    iVar2 = *(int *)(DAT_005ee794 + 0x80);
    while ((iVar2 != 0 && (param_1 < *(uint *)(iVar1 + iVar2 * 8 + -8)))) {
      iVar3 = iVar1 + iVar2 * 8;
      uVar4 = *(undefined4 *)(iVar3 + -4);
      puVar5 = (undefined4 *)(iVar1 + iVar2 * 8);
      *puVar5 = *(undefined4 *)(iVar3 + -8);
      puVar5[1] = uVar4;
      iVar2 = iVar2 + -1;
    }
    *(uint *)(iVar1 + iVar2 * 8) = param_1;
    *(uint *)(iVar1 + iVar2 * 8 + 4) = param_2;
    *(int *)(iVar1 + 0x80) = *(int *)(iVar1 + 0x80) + 1;
    *(uint *)(iVar1 + 0x84) = param_2 + *(int *)(iVar1 + 0x84);
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar6 = 0x6e;
      uVar7 = DAT_005ee648;
      param_3 = param_1;
      param_4 = param_2;
      FUN_0043d574(2,DAT_005ee79c,DAT_005ee798,DAT_005ee64c,0x6e,DAT_005ee648,param_1,param_2);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8800000,DAT_005ee880,DAT_005ee880,param_1,param_2,uVar7,param_3,param_4)
      ;
      uVar6 = param_2;
    }
  }
  return CONCAT44(uVar7,uVar6);
}

