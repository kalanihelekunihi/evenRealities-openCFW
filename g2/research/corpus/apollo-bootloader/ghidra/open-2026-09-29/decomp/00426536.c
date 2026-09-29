
int am_hal_mspi_interrupt_service(uint *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint *puVar2;
  uint uVar3;
  int *piVar4;
  int iVar5;
  uint uVar6;
  bool bVar7;
  uint *local_28;
  uint uStack_24;
  undefined4 uStack_20;
  undefined4 uStack_1c;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_00426c04)) {
    iVar1 = 2;
  }
  else {
    uVar3 = param_1[1];
    local_28 = param_1;
    uStack_24 = param_2;
    uStack_20 = param_3;
    uStack_1c = param_4;
    if ((char)param_1[0x20f] == '\0') {
      if (param_1[8] != 0) {
        piVar4 = (int *)(DAT_00426c08 + uVar3 * 0x8d0 + 0x828);
        param_1[9] = param_1[9] | param_2;
        if ((*piVar4 != 0) && (iVar1 = cmdq_get_status_427a56(*piVar4,&local_28), iVar1 == 0)) {
          *(undefined1 *)(param_1 + 0x20d) = 0;
          while (((char)param_1[0x20d] == '\0' && ((uint *)param_1[7] != local_28))) {
            param_1[7] = param_1[7] + 1;
            param_1[8] = param_1[8] - 1;
            uVar6 = (uint)(byte)param_1[7];
            if ((param_1[uVar6 + 10] != 0) &&
               ((*(code *)param_1[uVar6 + 10])(param_1[uVar6 + 0x10a],0),
               (char)param_1[0x20b] != '\x02')) {
              param_1[uVar6 + 10] = 0;
            }
          }
          if ((char)param_1[0x20d] == '\0') {
            if (((param_2 & 0x1880) != 0) || (uStack_1c._2_1_ != '\0')) {
              param_1[7] = param_1[7] + 1;
              param_1[8] = param_1[8] - 1;
              uVar6 = (uint)(byte)param_1[7];
              if ((param_1[uVar6 + 10] != 0) &&
                 ((*(code *)param_1[uVar6 + 10])(param_1[uVar6 + 0x10a],1),
                 (char)param_1[0x20b] != '\x02')) {
                param_1[uVar6 + 10] = 0;
              }
              iVar5 = cq_disable(param_1);
              iVar1 = DAT_00426804;
              if (iVar5 != 0) {
                return iVar5;
              }
              puVar2 = (uint *)(DAT_00426804 + uVar3 * 0x1000 + 0x100);
              *puVar2 = *puVar2 & 0xfffffffc;
              puVar2 = (uint *)(iVar1 + uVar3 * 0x1000 + 0x30);
              *puVar2 = *puVar2 & 0xbfffffff;
              puVar2 = (uint *)(iVar1 + uVar3 * 0x1000 + 0x30);
              *puVar2 = *puVar2 | 0x40000000;
              *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x2ac) =
                   *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x2ac);
              cmdq_error_resume_427b38(*piVar4);
              if ((param_1[8] != 0) && (iVar1 = FUN_00423f8e(param_1), iVar1 != 0)) {
                return iVar1;
              }
            }
            if ((param_1[8] == 0) && (iVar1 = cq_disable(param_1), iVar1 != 0)) {
              return iVar1;
            }
          }
        }
        if (((param_1[8] == 0) &&
            (puVar2 = (uint *)(DAT_00426804 + uVar3 * 0x1000 + 0x100),
            *puVar2 = *puVar2 & 0xfffffffc, *(char *)((int)param_1 + 0x8c9) != '\x04')) &&
           (iVar1 = clock_release(4,param_1[1] + 0x10 & 0xff), iVar1 != 0)) {
          return iVar1;
        }
      }
      iVar1 = 0;
    }
    else {
      param_1[9] = param_2 | param_1[9];
      iVar1 = DAT_00426804;
      if ((param_1[9] & 0x18c0) != 0) {
        do {
        } while (*(int *)(DAT_00426804 + param_1[1] * 0x1000 + 0x104) << 0x1f < 0);
        param_1[9] = param_1[9] | *(uint *)(DAT_00426804 + uVar3 * 0x1000 + 0x204);
        *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x208) = 0xffffffff;
        bVar7 = (param_1[9] & 0x1880) != 0;
        if (bVar7) {
          puVar2 = (uint *)(iVar1 + uVar3 * 0x1000 + 0x100);
          *puVar2 = *puVar2 & 0xfffffffc;
          puVar2 = (uint *)(iVar1 + uVar3 * 0x1000 + 0x30);
          *puVar2 = *puVar2 & 0xbfffffff;
          puVar2 = (uint *)(iVar1 + uVar3 * 0x1000 + 0x30);
          *puVar2 = *puVar2 | 0x40000000;
        }
        param_1[0x214] = param_1[0x214] + 1;
        param_1[0x210] = param_1[0x210] - 1;
        iVar5 = param_1[0x215] +
                (param_1[0x214] - param_1[0x212] * (param_1[0x214] / param_1[0x212])) * 0x18;
        if (*(int *)(iVar5 + 0x10) != 0) {
          (**(code **)(iVar5 + 0x10))(*(undefined4 *)(iVar5 + 0x14),bVar7);
          *(undefined4 *)(iVar5 + 0x10) = 0;
        }
        if (param_1[0x210] == 0) {
          *(undefined1 *)(param_1 + 0x20f) = 0;
          *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x100) = 0;
          *(uint *)(iVar1 + uVar3 * 0x1000 + 0x200) =
               *(uint *)(iVar1 + uVar3 * 0x1000 + 0x200) & 0xffffffbf;
          *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x2b4) = 0x80;
          if (((param_1[8] == 0) && (*(char *)((int)param_1 + 0x8c9) != '\x04')) &&
             (iVar1 = clock_release(4,param_1[1] + 0x10 & 0xff), iVar1 != 0)) {
            return iVar1;
          }
        }
        else {
          param_1[9] = 0;
          program_dma(param_1);
        }
      }
      iVar1 = 0;
    }
  }
  return iVar1;
}

