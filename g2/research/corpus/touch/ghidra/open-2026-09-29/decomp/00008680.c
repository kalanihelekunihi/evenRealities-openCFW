
int em_eeprom_extended_read_row_helper(int param_1,int param_2,ushort *param_3)

{
  ushort uVar1;
  ushort uVar2;
  bool bVar3;
  undefined4 uVar4;
  uint uVar5;
  int extraout_r1;
  int extraout_r1_00;
  int extraout_r1_01;
  int iVar6;
  uint uVar7;
  uint uVar8;
  int iVar9;
  int iVar10;
  uint uVar11;
  uint uVar12;
  int iVar13;
  uint uVar14;
  int iVar15;
  int local_40;
  
  uVar11 = (uint)*param_3;
  uVar1 = param_3[1];
  uVar4 = GetReadRowPointer(param_2,param_3);
  uVar5 = GetStoredSeqNum(param_1);
  if (uVar5 < uVar11) {
    local_40 = *(int *)(param_3 + 8);
  }
  else {
    local_40 = GetNextRowPointer(uVar4,param_3);
    uVar5 = uVar11;
  }
  iVar10 = DAT_00008804;
  if (uVar11 != 0) {
    uVar4 = __aeabi_uidiv(param_2 - *(int *)(param_3 + 8),uVar1);
    __aeabi_uidivmod(uVar4,uVar11);
    uVar11 = (uint)(uVar1 >> 1) * extraout_r1;
    uVar7 = (uVar1 >> 1) + uVar11;
    bVar3 = false;
    iVar10 = 0;
    for (uVar12 = 0; uVar12 < uVar5; uVar12 = uVar12 + 1) {
      if (uVar12 < uVar5 - 1) {
        uVar2 = param_3[1];
        iVar10 = CheckRowChecksum(local_40,uVar2);
        iVar13 = local_40;
        if (iVar10 != 0) {
          if ((char)param_3[7] != '\0') {
            iVar13 = (uint)*param_3 * (uint)(byte)param_3[6] * (uint)(uVar2 >> 2) * 4 + local_40;
            iVar10 = CheckRowChecksum(iVar13,uVar2);
          }
          goto LAB_0000879a;
        }
LAB_0000879e:
        uVar8 = *(uint *)(iVar13 + 8);
        iVar9 = *(int *)(iVar13 + 0xc);
        uVar14 = uVar8 + iVar9;
        if ((uVar8 < uVar7) && (uVar11 < uVar14)) {
          if (uVar8 < uVar11) {
            uVar2 = param_3[10];
            __aeabi_uidivmod(uVar8,(uint)uVar2);
            iVar6 = (uint)uVar2 - extraout_r1_00;
            iVar9 = uVar14 - uVar11;
            iVar15 = 0;
          }
          else {
            __aeabi_uidivmod(uVar8,param_3[10]);
            iVar15 = extraout_r1_01;
            if (uVar7 < uVar14) {
              iVar9 = uVar7 - uVar8;
              iVar6 = 0;
            }
            else {
              iVar6 = 0;
            }
          }
          if (bVar3) {
            memcpy((uint)(uVar1 >> 3) * 4 + param_1 + iVar15,iVar13 + iVar6 + 0x10,iVar9);
          }
          else {
            (*(code *)(*(undefined4 **)(param_3 + 0xe))[5])
                      (**(undefined4 **)(param_3 + 0xe),iVar13 + iVar6 + 0x10,iVar9,
                       (uint)(uVar1 >> 3) * 4 + param_1 + iVar15);
          }
        }
      }
      else {
        bVar3 = true;
        iVar13 = param_1;
LAB_0000879a:
        if (iVar10 == 0) goto LAB_0000879e;
      }
      local_40 = GetNextRowPointer(local_40,param_3);
    }
  }
  return iVar10;
}

