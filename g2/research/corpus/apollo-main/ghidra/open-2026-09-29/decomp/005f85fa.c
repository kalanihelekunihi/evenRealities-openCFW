
undefined4 tt_check_trickyness_sfnt_ids(int param_1)

{
  bool bVar1;
  bool bVar2;
  bool bVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  ushort uVar7;
  int iVar8;
  int local_a0 [30];
  int local_28;
  
  local_28 = param_1;
  FUN_0043c0e4(local_a0,0x74,0);
  bVar1 = false;
  bVar2 = false;
  bVar3 = false;
  uVar7 = 0;
  do {
    if (*(ushort *)(local_28 + 0x98) <= uVar7) {
      iVar5 = 0;
      while( true ) {
        if (0x1c < iVar5) {
          return 0;
        }
        if ((!bVar1) && (*(int *)(DAT_005f93a0 + iVar5 * 0x18 + 4) == 0)) {
          local_a0[iVar5] = local_a0[iVar5] + 1;
        }
        if ((!bVar2) && (*(int *)(DAT_005f93a0 + iVar5 * 0x18 + 0xc) == 0)) {
          local_a0[iVar5] = local_a0[iVar5] + 1;
        }
        if ((!bVar3) && (*(int *)(DAT_005f93a0 + iVar5 * 0x18 + 0x14) == 0)) {
          local_a0[iVar5] = local_a0[iVar5] + 1;
        }
        if (local_a0[iVar5] == 3) break;
        iVar5 = iVar5 + 1;
      }
      return 1;
    }
    iVar5 = 0;
    iVar6 = *(int *)(*(int *)(local_28 + 0x9c) + (uint)uVar7 * 0x10);
    if (iVar6 == DAT_005f9198) {
      iVar6 = 0;
      bVar1 = true;
LAB_005f8664:
      for (iVar8 = 0; iVar4 = DAT_005f93a0, iVar8 < 0x1d; iVar8 = iVar8 + 1) {
        if (*(int *)(*(int *)(local_28 + 0x9c) + (uint)uVar7 * 0x10 + 0xc) ==
            *(int *)(iVar8 * 0x18 + DAT_005f93a0 + iVar6 * 8 + 4)) {
          if (iVar5 == 0) {
            iVar5 = tt_get_sfnt_checksum(local_28,uVar7);
          }
          if (*(int *)(iVar4 + iVar8 * 0x18 + iVar6 * 8) == iVar5) {
            local_a0[iVar8] = local_a0[iVar8] + 1;
          }
          if (local_a0[iVar8] == 3) {
            return 1;
          }
        }
      }
    }
    else {
      if (iVar6 == DAT_005f9354) {
        iVar6 = 1;
        bVar2 = true;
        goto LAB_005f8664;
      }
      if (iVar6 == DAT_005f9358) {
        iVar6 = 2;
        bVar3 = true;
        goto LAB_005f8664;
      }
    }
    uVar7 = uVar7 + 1;
  } while( true );
}

