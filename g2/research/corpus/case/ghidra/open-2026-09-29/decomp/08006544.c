
/* WARNING: Type propagation algorithm not settling */

void case_process_frame_byte(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  char *pcVar2;
  char *pcVar3;
  undefined4 *puVar4;
  short sVar5;
  ushort uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  
  puVar4 = DAT_080066a4;
  pcVar3 = DAT_080066a0;
  pcVar2 = DAT_0800669c;
  if (*param_1 != DAT_08006698) {
    return;
  }
  uVar6 = *(ushort *)(DAT_0800669c + 2);
  uVar8 = (uint)uVar6;
  cVar1 = *DAT_0800669c;
  if (uVar8 == 0) {
    if (((cVar1 != 'Z') && (cVar1 != 'D')) && (cVar1 != 'd')) goto LAB_08006580;
LAB_08006566:
    DAT_080066a0[uVar8] = cVar1;
    *(ushort *)(pcVar2 + 2) = uVar6 + 1;
    pcVar2[1] = cVar1;
  }
  else if (uVar8 < 0x4b0) goto LAB_08006566;
  if ((cVar1 == '\n') && (iVar7 = case_starts_with_de(DAT_080066a0), iVar7 != 0)) {
LAB_08006674:
    osEventFlagsSet(*puVar4,8);
    goto LAB_08006686;
  }
  uVar8 = (uint)*(ushort *)(pcVar2 + 2);
  if (*pcVar3 != 'Z') {
    if (((uVar8 < 2) || (iVar7 = case_starts_with_de(DAT_080066a0), iVar7 != 0)) &&
       (*(ushort *)(pcVar2 + 2) < 0x3d)) goto LAB_08006580;
    goto LAB_08006682;
  }
  if (uVar8 == 1) goto LAB_08006580;
  if (uVar8 == 2) {
    if (pcVar3[1] == -0x5b) goto LAB_08006580;
LAB_08006682:
    case_validate_magic_state();
  }
  else {
    if (uVar8 == 3) {
      if (pcVar3[1] == -0x5b) {
        cVar1 = pcVar3[2];
        if (cVar1 == '\x7f') goto LAB_08006580;
joined_r0x080065f6:
        if (cVar1 == -0x31) goto LAB_08006580;
      }
      goto LAB_08006682;
    }
    if (uVar8 != 4) {
      if (uVar8 == 5) {
        if (pcVar3[2] == -0x31) {
          sVar5 = (ushort)(byte)pcVar3[3] + (ushort)(byte)pcVar3[4] * 0x100;
          iVar7 = case_read_controller_blocking(DAT_080066a8,pcVar3 + 5,sVar5,0x14,param_4);
          if (iVar7 != 3) {
            uVar6 = *(short *)(pcVar2 + 2) + sVar5;
            goto LAB_08006648;
          }
        }
        else if (pcVar3[2] == '\x7f') goto LAB_08006580;
      }
      else {
        if (pcVar3[2] == '\x7f') {
          uVar9 = (byte)pcVar3[3] + 5;
        }
        else {
          if (pcVar3[2] != -0x31) goto LAB_08006682;
          uVar9 = (ushort)((ushort)(byte)pcVar3[4] * 0x100 + (ushort)(byte)pcVar3[3]) + 6;
        }
        if (uVar9 == uVar8) goto LAB_08006674;
        if (uVar8 <= uVar9) goto LAB_08006686;
      }
      goto LAB_08006682;
    }
    cVar1 = pcVar3[2];
    if (cVar1 != '\x7f') goto joined_r0x080065f6;
    iVar7 = case_read_controller_blocking(DAT_080066a8,pcVar3 + 4,pcVar3[3],10,param_4);
    if (iVar7 == 3) goto LAB_08006682;
    uVar6 = (ushort)(byte)pcVar3[3] + *(short *)(pcVar2 + 2);
LAB_08006648:
    *(ushort *)(pcVar2 + 2) = uVar6;
    pcVar2[1] = pcVar3[uVar6 - 1];
  }
LAB_08006686:
  if (*(short *)(pcVar2 + 2) == 0x4b0) {
    case_validate_magic_state();
  }
LAB_08006580:
  iVar7 = case_start_context_transfer(DAT_080066a8,DAT_0800669c,1);
  if (iVar7 != 0) {
    osEventFlagsSet(*puVar4,0x40);
  }
  return;
}

