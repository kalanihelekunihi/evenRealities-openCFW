
char _evenOtaSetFwAddr(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  int *piVar1;
  undefined4 uVar2;
  uint uVar3;
  int iVar4;
  int iVar5;
  char cVar6;
  
  iVar5 = DAT_00445430;
  *(undefined4 *)(DAT_00445430 + 0x38) = 0;
  *(undefined4 *)(iVar5 + 0x3c) = 0;
  *(undefined4 *)(DAT_00444c98 + 100) = 0;
  uVar3 = DAT_00445438;
  uVar2 = DAT_00445434;
  if (*(int *)(iVar5 + 0x2c) == 0) {
    if (DAT_00445438 < *(uint *)(iVar5 + 0xc)) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        param_4 = *(undefined4 *)(iVar5 + 0xc);
        param_2 = DAT_0044543c;
        param_3 = uVar3;
        FUN_0043d574(1,DAT_00444dec,DAT_00444de8,DAT_00445440,0x243,DAT_0044543c,uVar3,param_4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_00445444,DAT_00445444,uVar3,*(undefined4 *)(iVar5 + 0xc),
                            param_2,param_3,param_4);
      }
      return '\0';
    }
    if (DAT_00445448 <= *(uint *)(iVar5 + 0xc)) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00444dec,DAT_00444de8,DAT_00445440,0x24a,DAT_0044544c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00445450);
      }
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00444dec,DAT_00444de8,DAT_00445440,0x24c,DAT_00445454,0x1f4000,
                     *(undefined4 *)(iVar5 + 0xc));
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4800000,DAT_00445458,DAT_00445458,0x1f4000,
                            *(undefined4 *)(iVar5 + 0xc));
      }
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00444dec,DAT_00444de8,DAT_00445440,0x24d,DAT_0044557c);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00445580,DAT_00445580);
      }
      return '\0';
    }
    *DAT_0044542c = DAT_00445584;
    *(undefined4 *)(iVar5 + 0x38) = uVar2;
    cVar6 = '\x01';
  }
  else {
    if (*(int *)(iVar5 + 0x2c) == 1) {
      *DAT_0044542c = DAT_00445588;
      return '\x01';
    }
    if ((*(int *)(iVar5 + 0x2c) == 3) && (*(int *)(iVar5 + 0x28) == 1)) {
      *DAT_0044542c = DAT_00445584;
      *(undefined4 *)(iVar5 + 0x38) = 0x410000;
      cVar6 = '\x01';
    }
    else {
      cVar6 = '\0';
    }
  }
  piVar1 = DAT_0044542c;
  if (cVar6 != '\0') {
    if (*(int *)(*DAT_0044542c + 8) == 0) {
      iVar4 = 0;
    }
    else {
      iVar4 = (**(code **)(*DAT_0044542c + 8))();
    }
    if (iVar4 == 0) {
      if (*(int *)(*piVar1 + 0x10) == 0) {
        iVar4 = 0;
      }
      else {
        iVar4 = (**(code **)(*piVar1 + 0x10))();
      }
      if (iVar4 != 0) {
        if (*(int *)(*piVar1 + 0xc) != 0) {
          (**(code **)(*piVar1 + 0xc))();
        }
        cVar6 = '\0';
      }
      semantic_OtaEraseRange(*(undefined4 *)(iVar5 + 0x38),*(undefined4 *)(iVar5 + 0xc));
      if (*(int *)(*piVar1 + 0x14) != 0) {
        (**(code **)(*piVar1 + 0x14))();
      }
    }
    else {
      cVar6 = '\0';
    }
  }
  return cVar6;
}

