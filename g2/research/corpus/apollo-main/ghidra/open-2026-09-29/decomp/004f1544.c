
void FUN_004f1544(void)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  int *piVar4;
  int *piVar5;
  int *piVar6;
  undefined4 *puVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  int iVar13;
  int iVar14;
  undefined4 uVar15;
  undefined4 in_r3;
  int local_88;
  int local_84;
  int local_80;
  int local_7c;
  int local_78;
  int local_74;
  int local_70;
  undefined4 local_68;
  undefined4 local_58;
  undefined4 uStack_28;
  
  piVar2 = DAT_004f1a20;
  piVar1 = DAT_004f19e8;
  uStack_28 = in_r3;
  if ((*DAT_004f1a20 == 0) || (*DAT_004f188c == 0)) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      local_84 = DAT_004f1aa0;
      local_88 = 0x34f;
      FUN_0043d574(2,DAT_004f18a0,DAT_004f189c,DAT_004f1aa4);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004f1aa8,DAT_004f1aa8);
    }
  }
  else if ((*DAT_004f19e8 < 0) || (*DAT_004f188c <= *DAT_004f19e8)) {
    iVar8 = FUN_0043d0ce();
    if (iVar8 << 0x1e < 0) {
      local_80 = *piVar1;
      local_84 = DAT_004f1aac;
      local_88 = 0x353;
      FUN_0043d574(2,DAT_004f18a0,DAT_004f189c,DAT_004f1aa4);
    }
    iVar8 = FUN_0043d0ce();
    if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
      compress_log_output(0x8400000,DAT_004f1ab0,DAT_004f1ab0,*piVar1);
    }
  }
  else {
    local_88 = *(int *)(DAT_004f1890 + *DAT_004f19e8 * 4);
    if (local_88 == 0) {
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        local_84 = DAT_004f1ab4;
        local_88 = 0x359;
        FUN_0043d574(2,DAT_004f18a0,DAT_004f189c,DAT_004f1aa4);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        compress_log_output(0x8000000,DAT_004f2208,DAT_004f2208);
      }
    }
    else {
      iVar8 = FUN_0044e498(*DAT_004f1a20);
      iVar9 = FUN_0043fce0(local_88);
      iVar10 = FUN_0043fc70(local_88);
      iVar11 = FUN_0043fc70(*piVar2);
      iVar12 = FUN_0043fce0(*piVar2);
      puVar7 = DAT_004f220c;
      local_80 = FUN_0043fc70(*DAT_004f220c);
      iVar13 = FUN_0043fce0(*puVar7);
      local_84 = FUN_004eff9e(*piVar2,0);
      iVar14 = FUN_004eff94(*piVar2,0);
      *DAT_004f1a3c = iVar10 + local_84 + iVar11 + local_80;
      piVar3 = DAT_004f1a44;
      *DAT_004f1a44 = (iVar9 + iVar14 + iVar12 + iVar13) - iVar8;
      piVar4 = DAT_004f1a48;
      iVar8 = FUN_0043fd9e(local_88);
      *piVar4 = iVar8;
      piVar5 = DAT_004f1a4c;
      iVar8 = FUN_0043fdda(local_88);
      *piVar5 = iVar8;
      piVar6 = DAT_004f1a64;
      *DAT_004f1a64 = *piVar1;
      iVar8 = FUN_0043d0ce();
      if (iVar8 << 0x1e < 0) {
        local_70 = *piVar6;
        local_74 = *piVar5;
        local_78 = *piVar4;
        local_7c = *piVar3;
        local_80 = *DAT_004f1a3c;
        local_84 = DAT_004f2280;
        local_88 = 0x377;
        FUN_0043d574(3,DAT_004f18a0,DAT_004f189c,DAT_004f1aa4);
      }
      iVar8 = FUN_0043d0ce();
      if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
        local_7c = *piVar6;
        local_80 = *piVar5;
        local_84 = *piVar4;
        local_88 = *piVar3;
        compress_log_output(0xd400000,DAT_004f2284,DAT_004f2284,*DAT_004f1a3c);
      }
      if (*piVar2 != 0) {
        FUN_0043ded4(*piVar2,1);
      }
      piVar1 = DAT_004f1a74;
      iVar8 = FUN_0043de82(*DAT_004f230c);
      *piVar1 = iVar8;
      if (*piVar1 == 0) {
        iVar8 = FUN_0043d0ce();
        if (iVar8 << 0x1e < 0) {
          local_84 = DAT_004f2310;
          local_88 = 0x381;
          FUN_0043d574(1,DAT_004f18a0,DAT_004f189c,DAT_004f1aa4);
        }
        iVar8 = FUN_0043d0ce();
        if ((iVar8 << 0x1f < 0) || (iVar8 = FUN_0043d0ce(), iVar8 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004f2314,DAT_004f2314);
        }
        if (*piVar2 != 0) {
          FUN_0043dfa4(*piVar2,1);
        }
      }
      else {
        FUN_0043f09a(*piVar1,*DAT_004f1a3c,*piVar3);
        FUN_0043f4c0(*piVar1,*piVar4,*piVar5);
        FUN_0044129e(*piVar1,0,0);
        FUN_0044131c(*piVar1,2,0);
        uVar15 = FUN_0044104c(0xffffff);
        FUN_004412ec(*piVar1,uVar15,0);
        FUN_0044146a(*piVar1,6,0);
        FUN_004effa8(*piVar1,0,0);
        FUN_0043dfa4(*piVar1,0x10);
        *DAT_004f19f8 = 1;
        *DAT_004f1a60 = 1;
        *DAT_004f1a94 = 0;
        FUN_004503d6(&local_88);
        local_88 = *piVar1;
        local_84 = DAT_004f23d0;
        FUN_004506ce(&local_88,0,1000);
        local_58 = 300;
        local_68 = DAT_004f1a34;
        local_78 = DAT_004f251c;
        FUN_00450408(&local_88);
      }
    }
  }
  return;
}

