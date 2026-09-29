
undefined8 FUN_00550968(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint *puVar1;
  short sVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  
  iVar5 = DAT_00550ff4;
  uVar6 = param_1;
  if (*(int *)(DAT_00550ff4 + 0x3c) != 0) {
    iVar4 = service_ancc_message_count_get();
    puVar1 = DAT_00550f7c;
    if (iVar4 == 0) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        uVar6 = 0x399;
        param_2 = DAT_00551460;
        FUN_0043d574(2,DAT_005514b8,DAT_0055148c,DAT_00551488,0x399,DAT_00551460,param_3,param_4);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_00551490,DAT_00551490);
      }
      *DAT_00550d38 = 0;
    }
    else if (((int)param_1 < 0) || (iVar4 <= (int)param_1)) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        uVar6 = 0x3a0;
        param_2 = DAT_005514d8;
        FUN_0043d574(2,DAT_005514b8,DAT_0055148c,DAT_00551488,0x3a0,DAT_005514d8,param_1,iVar4 + -1)
        ;
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        uVar6 = iVar4 - 1;
        compress_log_output(0x8800000,DAT_005514dc,DAT_005514dc,param_1);
      }
      *DAT_00550d38 = 0;
    }
    else {
      sVar2 = FUN_00550170(*DAT_00550f7c & 0xff);
      sVar3 = FUN_00550170(param_1 & 0xff);
      if (sVar3 < 0) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          uVar6 = 0x3a8;
          param_2 = DAT_005514e0;
          FUN_0043d574(2,DAT_005514b8,DAT_0055148c,DAT_00551488,0x3a8,DAT_005514e0,param_1,param_4);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_005514e4,DAT_005514e4,param_1);
        }
        *DAT_00550d38 = 0;
      }
      else {
        *DAT_00550d38 = 1;
        iVar4 = FUN_00509694((int)sVar3 - (int)sVar2);
        iVar4 = (iVar4 + -1) * 0x32 + *DAT_005514d4;
        if ((int)sVar3 == *puVar1) {
          iVar4 = 10;
        }
        else {
          *puVar1 = (int)sVar3;
          FUN_00550e2e(*puVar1,1);
        }
        FUN_00550694(*(undefined4 *)(iVar5 + 0x3c),sVar3 * 0xd6,iVar4);
      }
    }
  }
  return CONCAT44(param_2,uVar6);
}

