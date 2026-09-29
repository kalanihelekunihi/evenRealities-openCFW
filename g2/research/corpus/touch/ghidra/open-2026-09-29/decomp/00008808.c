
int ReadExtendedMode(int param_1,int param_2,int param_3,ushort *param_4)

{
  undefined4 *puVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  int iVar7;
  uint uVar8;
  int local_2c [2];
  
  uVar2 = __aeabi_uidiv(param_3 + -1,param_4[0xb]);
  CheckLastWrittenRowIntegrity(local_2c,param_4);
  iVar5 = *(int *)(param_4 + 0xc);
  iVar3 = 0;
  iVar7 = 0;
  for (uVar8 = 0; uVar8 < uVar2 + 1; uVar8 = uVar8 + 1) {
    iVar5 = GetNextRowPointer(iVar5,param_4);
    puVar1 = DAT_00008908;
    iVar3 = local_2c[0] + 1;
    local_2c[0] = iVar3;
    memset(DAT_00008908,0,param_4[1]);
    puVar1[1] = iVar3;
    puVar1[2] = param_1;
    puVar1[3] = (uint)param_4[0xb];
    if (uVar2 == uVar8) {
      DAT_00008908[3] = param_3;
    }
    puVar1 = DAT_00008908;
    memcpy(DAT_00008908 + 4,param_2,DAT_00008908[3]);
    CopyHistoricData(puVar1,iVar5,param_4);
    iVar7 = em_eeprom_extended_read_row_helper(puVar1,iVar5,param_4);
    uVar4 = CalculateRowChecksum(puVar1,param_4[1]);
    *puVar1 = uVar4;
    iVar3 = em_eeprom_row_read_helper(iVar5,puVar1,param_4);
    if (iVar3 != 0) break;
    if ((char)param_4[7] != '\0') {
      iVar3 = em_eeprom_row_read_helper
                        (iVar5 + (uint)*param_4 * (uint)(byte)param_4[6] * (uint)(param_4[1] >> 2) *
                                 4,DAT_00008908,param_4);
    }
    if (iVar3 != 0) break;
    *(int *)(param_4 + 0xc) = iVar5;
    uVar6 = (uint)param_4[0xb];
    param_3 = param_3 - uVar6;
    param_1 = param_1 + uVar6;
    param_2 = param_2 + uVar6;
  }
  if (iVar3 == 0) {
    iVar3 = iVar7;
  }
  return iVar3;
}

