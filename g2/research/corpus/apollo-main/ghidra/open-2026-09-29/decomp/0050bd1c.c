
void FUN_0050bd1c(void)

{
  int *piVar1;
  undefined4 *puVar2;
  int iVar3;
  int iVar4;
  undefined4 in_r3;
  int iVar5;
  undefined1 local_28 [4];
  undefined4 local_24;
  undefined1 auStack_20 [12];
  undefined4 uStack_14;
  
  uStack_14 = in_r3;
  FUN_0050c3c0();
  iVar3 = FUN_0050c654();
  piVar1 = DAT_0050c524;
  if (iVar3 == 0) {
    if (((*DAT_0050c520 == 1) && (*DAT_0050c524 != 0)) &&
       (iVar3 = ui_common_api_fn_00509dfa(*DAT_0050c524), iVar3 == 0)) {
      FUN_0043c0e4(auStack_20,10,0);
      FUN_0043c0e4(auStack_20,10,0);
      ui_common_api_fn_00509e14(*piVar1,auStack_20,7);
      iVar3 = ui_onboarding_main_sub_004A979C(auStack_20,0,local_28);
      if (iVar3 == 0) {
        FUN_0050a670(local_28[0],local_24);
      }
    }
  }
  else {
    iVar3 = FUN_0050c476(0);
    if ((iVar3 != 0) && (*(char *)(iVar3 + 0x29) != '\0')) {
      FUN_0050c6cc();
    }
    iVar3 = DAT_0050bf98;
    *(undefined1 *)(DAT_0050bf98 + 0xc4) = 1;
    puVar2 = DAT_0050c6c4;
    *DAT_0050c6c4 = 0xffffffff;
    *(undefined1 *)(puVar2 + 5) = 1;
    for (iVar5 = 0; iVar5 < 4; iVar5 = iVar5 + 1) {
      iVar4 = *(int *)(iVar5 * 0x30 + iVar3 + 0x20);
      if (iVar4 == 0) {
        FUN_0050c6e2(iVar3 + iVar5 * 0x30);
        puVar2[iVar5 + 1] = 0x120;
      }
      else if (iVar4 == 0x120) {
        puVar2[iVar5 + 1] = 0x240;
      }
      else if (iVar4 == 0x240) {
        FUN_0050c4ac(iVar3 + iVar5 * 0x30);
        puVar2[iVar5 + 1] = DAT_0050c864;
      }
      else if (iVar4 == DAT_0050c864) {
        FUN_0050c6e2(iVar3 + iVar5 * 0x30);
        puVar2[iVar5 + 1] = 0;
      }
    }
    FUN_0050c7a8(0xffffffff,400);
  }
  return;
}

