
int touch_eeprom_4fe0_read_extended(uint param_1,int param_2,int param_3,ushort *param_4)

{
  ushort uVar1;
  ushort uVar2;
  ushort uVar3;
  ushort uVar4;
  int iVar5;
  int iVar6;
  undefined4 uVar7;
  int iVar8;
  int extraout_r1;
  uint uVar9;
  int extraout_r1_00;
  uint uVar10;
  uint uVar11;
  uint uVar12;
  uint uVar13;
  int iVar14;
  uint uVar15;
  int iVar16;
  int iVar17;
  uint local_58;
  int local_54;
  int local_50;
  undefined1 auStack_2c [8];
  
  uVar1 = *param_4;
  memset(param_2,0);
  CheckLastWrittenRowIntegrity(auStack_2c,param_4);
  uVar10 = param_3 + param_1;
  uVar2 = param_4[10];
  iVar5 = __aeabi_uidiv(uVar10 - 1,uVar2);
  iVar6 = __aeabi_uidiv(param_1,uVar2);
  iVar16 = *(int *)(param_4 + 8) + iVar6 * (uint)param_4[1];
  local_50 = 0;
  uVar11 = param_1;
  iVar17 = param_2;
  local_54 = param_3;
  for (uVar15 = 0; uVar15 < (iVar5 - iVar6) + 1U; uVar15 = uVar15 + 1) {
    uVar2 = param_4[6];
    if (1 < (byte)uVar2) {
      iVar16 = GetReadRowPointer(*(undefined4 *)(param_4 + 0xc),param_4);
      for (uVar13 = 0; uVar4 = *param_4, uVar13 < uVar4; uVar13 = uVar13 + 1) {
        iVar16 = GetNextRowPointer(iVar16,param_4);
        uVar3 = param_4[1];
        uVar7 = __aeabi_uidiv(iVar16 - *(int *)(param_4 + 8),uVar3);
        __aeabi_uidivmod(uVar7,(uint)uVar4);
        uVar12 = (uint)(uVar3 >> 1);
        uVar9 = uVar12 * extraout_r1;
        if ((uVar9 <= uVar11) && (uVar11 < uVar12 + uVar9)) break;
      }
    }
    uVar13 = (uint)param_4[10];
    __aeabi_uidivmod(uVar11,uVar13);
    iVar14 = uVar13 - extraout_r1_00;
    if ((uint)(iVar5 - iVar6) <= uVar15) {
      iVar14 = local_54;
    }
    uVar4 = param_4[1];
    local_58 = CheckRowChecksum(iVar16,uVar4);
    if (local_58 == 0) {
LAB_000083a8:
      (*(code *)(*(undefined4 **)(param_4 + 0xe))[5])
                (**(undefined4 **)(param_4 + 0xe),iVar16 + uVar13 + extraout_r1_00,iVar14,iVar17);
    }
    else {
      if ((char)param_4[7] != '\0') {
        iVar16 = iVar16 + (uint)(uVar4 >> 2) * (uint)*param_4 * (uint)(byte)uVar2 * 4;
        iVar8 = CheckRowChecksum(iVar16,uVar4);
        if (iVar8 == 0) {
          local_58 = DAT_00008550;
          goto LAB_000083a8;
        }
      }
      memset(iVar17,0,iVar14);
      iVar8 = GetStoredSeqNum(iVar16);
      if (iVar8 == 0) {
        local_58 = GetStoredRowChecksum(iVar16);
        if (local_58 != 0) {
          local_58 = DAT_0000854c;
        }
      }
      else {
        local_58 = DAT_0000854c;
      }
    }
    if ((byte)param_4[6] < 2) {
      iVar16 = GetNextRowPointer(iVar16,param_4);
    }
    local_54 = local_54 - iVar14;
    uVar11 = uVar11 + iVar14;
    iVar17 = iVar17 + iVar14;
    if ((local_58 != DAT_0000854c) && (local_50 != 0)) {
      local_58 = local_50;
    }
    local_50 = local_58;
  }
  iVar17 = GetReadRowPointer(*(undefined4 *)(param_4 + 0xc),param_4);
  uVar11 = 0;
  do {
    if (uVar1 <= uVar11) {
      return local_50;
    }
    iVar17 = GetNextRowPointer(iVar17,param_4);
    uVar15 = (uint)param_4[1];
    iVar6 = CheckRowChecksum(iVar17,uVar15);
    iVar5 = iVar17;
    if (iVar6 == 0) {
LAB_000084ba:
      local_58 = *(uint *)(iVar5 + 8);
      uVar15 = *(int *)(iVar5 + 0xc) + local_58;
      if ((local_58 < uVar10) && (param_1 < uVar15)) {
        if (param_1 < local_58) {
          iVar16 = local_58 - param_1;
          iVar6 = 0;
        }
        else {
          iVar16 = 0;
          iVar6 = param_1 - local_58;
          local_58 = param_1;
        }
        uVar13 = uVar10;
        if (uVar15 < uVar10) {
          uVar13 = uVar15;
        }
        (*(code *)(*(undefined4 **)(param_4 + 0xe))[5])
                  (**(undefined4 **)(param_4 + 0xe),iVar5 + iVar6 + 0x10,uVar13 - local_58,
                   iVar16 + param_2);
      }
    }
    else {
      if ((char)param_4[7] != '\0') {
        iVar5 = uVar15 * (uint)*param_4 * (uint)(byte)param_4[6];
        iVar5 = iVar17 + ((int)((iVar5 >> 0x1f & 3U) + iVar5) >> 2) * 4;
        iVar6 = CheckRowChecksum(iVar5,uVar15);
      }
      if (iVar6 == 0) goto LAB_000084ba;
    }
    uVar11 = uVar11 + 1;
  } while( true );
}

