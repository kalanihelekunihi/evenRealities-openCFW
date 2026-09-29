
int touch_eeprom_57e0_erase_adapter(ushort *param_1)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  int local_24;
  int local_1c;
  
  iVar4 = (uint)*param_1 * (uint)(byte)param_1[6];
  memset(DAT_00008bf0,0,param_1[1]);
  if (*(char *)((int)param_1 + 0xd) == '\0') {
    CheckLastWrittenRowIntegrity(&local_1c,param_1);
    iVar2 = GetNextRowPointer(*(undefined4 *)(param_1 + 0xc),param_1);
    puVar1 = DAT_00008bf0;
    DAT_00008bf0[1] = local_1c + 1;
    uVar3 = CalculateRowChecksum(puVar1,param_1[1]);
    *puVar1 = uVar3;
    local_24 = em_eeprom_row_read_helper(iVar2,puVar1,param_1);
    iVar6 = local_24;
    if ((((char)param_1[7] == '\0') ||
        (iVar6 = em_eeprom_row_read_helper
                           (iVar2 + iVar4 * (uint)(param_1[1] >> 2) * 4,DAT_00008bf0,param_1),
        local_24 == 0)) && (local_24 = iVar6, local_24 == 0)) {
      *(int *)(param_1 + 0xc) = iVar2;
      for (uVar5 = 0; uVar5 < iVar4 - 1U; uVar5 = uVar5 + 1) {
        iVar2 = GetNextRowPointer(iVar2,param_1);
        iVar6 = touch_eeprom_560c_write_row(iVar2,DAT_00008bf0,param_1);
        if (local_24 != 0) {
          iVar6 = local_24;
        }
        local_24 = iVar6;
        if (((char)param_1[7] != '\0') &&
           (iVar6 = touch_eeprom_560c_write_row
                              (iVar2 + iVar4 * (uint)(param_1[1] >> 2) * 4,DAT_00008bf0,param_1),
           local_24 == 0)) {
          local_24 = iVar6;
        }
      }
    }
  }
  else {
    iVar4 = __aeabi_uidiv((uint)param_1[1] * iVar4 + -1,*(undefined4 *)(param_1 + 2));
    iVar6 = *(int *)(param_1 + 8);
    local_24 = 0;
    for (uVar5 = 0; uVar5 < iVar4 + 1U; uVar5 = uVar5 + 1) {
      iVar2 = touch_eeprom_560c_write_row(iVar6,DAT_00008bf0,param_1);
      if (local_24 == 0) {
        local_24 = iVar2;
      }
      iVar6 = iVar6 + (*(uint *)(param_1 + 2) & 0xfffffffc);
    }
  }
  return local_24;
}

