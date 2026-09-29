
void FUN_0050ba64(void)

{
  bool bVar1;
  int *piVar2;
  undefined4 *puVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 in_r3;
  uint local_30;
  undefined4 local_2c;
  int local_28 [3];
  undefined4 uStack_1c;
  
  uStack_1c = in_r3;
  FUN_0050c3c0();
  iVar4 = FUN_0050c528();
  piVar2 = DAT_0050c524;
  if (iVar4 == 0) {
    if (((*DAT_0050c520 == 1) && (*DAT_0050c524 != 0)) &&
       (iVar4 = ui_common_api_fn_00509dfa(*DAT_0050c524), iVar4 == 0)) {
      FUN_0043c0e4(local_28,10,0);
      FUN_0043c0e4(local_28,10,0);
      ui_common_api_fn_00509e14(*piVar2,local_28,7);
      iVar4 = ui_onboarding_main_sub_004A979C(local_28,0,&local_30);
      if (iVar4 == 0) {
        FUN_0050a670(local_30 & 0xff,local_2c);
      }
    }
  }
  else {
    iVar4 = FUN_0050c476(0x120);
    if ((((iVar4 != 0) && (*(char *)(iVar4 + 0x29) == '\0')) && (iVar5 = FUN_0050c8cc(), -1 < iVar5)
        ) && (iVar4 = FUN_0050c314(iVar4,iVar5), iVar4 == 0)) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_2c = DAT_0050c648;
        local_30 = 0x6be;
        local_28[0] = iVar5;
        FUN_0043d574(2,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c64c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0050c650,DAT_0050c650,iVar5);
      }
    }
    iVar4 = FUN_0050c476(0x240);
    if (((iVar4 != 0) && (*(char *)(iVar4 + 0x29) == '\0')) &&
       ((iVar5 = FUN_0050c8cc(), -1 < iVar5 && (iVar4 = FUN_0050c314(iVar4,iVar5), iVar4 == 0)))) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        local_2c = DAT_0050c6bc;
        local_30 = 0x6cd;
        local_28[0] = iVar5;
        FUN_0043d574(2,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c64c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_0050c6c0,DAT_0050c6c0,iVar5);
      }
    }
    iVar4 = DAT_0050bf98;
    *(undefined1 *)(DAT_0050bf98 + 0xc4) = 1;
    puVar3 = DAT_0050c6c4;
    *DAT_0050c6c4 = 1;
    *(undefined1 *)(puVar3 + 5) = 1;
    for (iVar5 = 0; iVar5 < 4; iVar5 = iVar5 + 1) {
      iVar6 = *(int *)(iVar5 * 0x30 + iVar4 + 0x20);
      if (iVar6 == 0) {
        if (*(char *)(iVar5 * 0x30 + iVar4 + 0x29) != '\0') {
          *(undefined1 *)(iVar5 * 0x30 + iVar4 + 0x27) = 1;
          FUN_0050c6e2(iVar4 + iVar5 * 0x30);
        }
        puVar3[iVar5 + 1] = DAT_0050c864;
      }
      else if (iVar6 == 0x120) {
        FUN_0050c6e2(iVar4 + iVar5 * 0x30);
        puVar3[iVar5 + 1] = 0;
      }
      else if (iVar6 == 0x240) {
        puVar3[iVar5 + 1] = 0x120;
      }
      else if (iVar6 == DAT_0050c864) {
        bVar1 = false;
        if ((*(char *)(iVar5 * 0x30 + iVar4 + 0x29) != '\0') &&
           (*(char *)(iVar5 * 0x30 + iVar4 + 0x27) != '\0')) {
          bVar1 = true;
        }
        FUN_0050c4ac(iVar5 * 0x30 + iVar4);
        puVar3[iVar5 + 1] = 0x240;
        if (bVar1) {
          FUN_0050c288();
          FUN_0050c3c0();
        }
        iVar6 = FUN_0050c8cc();
        if ((-1 < iVar6) && (iVar7 = FUN_0050c314(iVar4 + iVar5 * 0x30,iVar6), iVar7 == 0)) {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            local_2c = DAT_0050c6c8;
            local_30 = 0x715;
            local_28[0] = iVar6;
            FUN_0043d574(2,DAT_0050c2fc,DAT_0050c2f8,DAT_0050c64c);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x8400000,DAT_0050c764,DAT_0050c764,iVar6);
          }
        }
      }
    }
    FUN_0050c7a8(1,400);
  }
  return;
}

