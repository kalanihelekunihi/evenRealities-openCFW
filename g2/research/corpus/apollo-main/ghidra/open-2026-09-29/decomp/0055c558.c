
int FUN_0055c558(uint *param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  undefined4 uVar2;
  uint *puVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  uint uVar7;
  uint *local_30;
  uint uStack_2c;
  undefined4 uStack_28;
  undefined4 uStack_24;
  
  iVar5 = 0;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055cc14)) {
    iVar5 = 2;
  }
  else {
    uVar4 = param_1[1];
    local_30 = param_1;
    uStack_2c = param_2;
    uStack_28 = param_3;
    uStack_24 = param_4;
    if ((char)param_1[0x20f] == '\0') {
      if (param_1[9] != 0) {
        if ((param_1[0x20a] != 0) && (iVar5 = FUN_0053901a(param_1[0x20a],&local_30), iVar5 == 0)) {
          *(undefined1 *)(param_1 + 0x20d) = 0;
          while (((uint *)param_1[7] != local_30 && ((char)param_1[0x20d] == '\0'))) {
            param_1[7] = param_1[7] + 1;
            param_1[9] = param_1[9] - 1;
            uVar7 = (uint)(byte)param_1[7];
            if ((param_1[uVar7 + 10] != 0) &&
               ((*(code *)param_1[uVar7 + 10])(param_1[uVar7 + 0x10a],0),
               (char)param_1[0x20b] != '\x02')) {
              param_1[uVar7 + 10] = 0;
            }
          }
          if (((char)param_1[0x20d] == '\0') && ((param_2 & 0x4a7c) != 0)) {
            param_1[7] = param_1[7] + 1;
            param_1[9] = param_1[9] - 1;
            uVar7 = (uint)(byte)param_1[7];
            if (param_1[uVar7 + 10] != 0) {
              uVar2 = FUN_0055bd70(uVar4,param_2);
              (*(code *)param_1[uVar7 + 10])(param_1[uVar7 + 0x10a],uVar2);
              if ((char)param_1[0x20b] != '\x02') {
                param_1[uVar7 + 10] = 0;
              }
            }
            iVar6 = DAT_0055cf38;
            puVar3 = (uint *)(DAT_0055cf38 + uVar4 * 0x1000 + 0x228);
            *puVar3 = *puVar3 & 0xfffffffe;
            puVar3 = (uint *)(iVar6 + uVar4 * 0x1000 + 0x218);
            *puVar3 = *puVar3 & 0xfffffffe;
            *(undefined4 *)(iVar6 + uVar4 * 0x1000 + 0x224) = 0;
            FUN_0055bdac(param_1,param_2 & 0x4a7c);
            FUN_005390fc(param_1[0x20a]);
            if (param_1[9] != 0) {
              FUN_0055c13a(param_1);
            }
          }
          if (param_1[9] == 0) {
            FUN_0055c168(param_1);
          }
        }
        iVar6 = DAT_0055cf38;
        if (param_1[9] == 0) {
          *(undefined4 *)(DAT_0055cf38 + uVar4 * 0x1000 + 0x200) = 0;
          *(undefined4 *)(iVar6 + uVar4 * 0x1000 + 0x208) = 0xffffffff;
          *(uint *)(iVar6 + uVar4 * 0x1000 + 0x200) = param_1[5];
        }
      }
    }
    else {
      param_1[6] = param_2 | param_1[6];
      iVar5 = DAT_0055cf38;
      if ((param_1[6] & 0x801) != 0) {
        if ((*(int *)(DAT_0055cf38 + uVar4 * 0x1000 + 0x218) << 0x1f < 0) &&
           ((param_1[6] & 0x4e7c) == 0)) {
          bVar1 = false;
        }
        else {
          bVar1 = true;
        }
        if (bVar1) {
          param_1[0x214] = param_1[0x214] + 1;
          param_1[0x210] = param_1[0x210] - 1;
          iVar6 = param_1[0x215] +
                  (param_1[0x214] - param_1[0x212] * (param_1[0x214] / param_1[0x212])) * 0x20;
          if (*(int *)(iVar6 + 0x18) != 0) {
            uVar2 = FUN_0055bd70(uVar4,param_1[6]);
            (**(code **)(iVar6 + 0x18))(*(undefined4 *)(iVar6 + 0x1c),uVar2);
            *(undefined4 *)(iVar6 + 0x18) = 0;
          }
          if ((param_1[6] & 0x4a7c) != 0) {
            puVar3 = (uint *)(iVar5 + uVar4 * 0x1000 + 0x218);
            *puVar3 = *puVar3 & 0xfffffffe;
            *(undefined4 *)(iVar5 + uVar4 * 0x1000 + 0x224) = 0;
            FUN_0055bdac(param_1,param_1[6] & 0x4a7c);
          }
          if (param_1[0x210] == 0) {
            *(undefined1 *)(param_1 + 0x20f) = 0;
            *(uint *)(iVar5 + uVar4 * 0x1000 + 0x200) =
                 *(uint *)(iVar5 + uVar4 * 0x1000 + 0x200) & DAT_0055cf3c;
            *(undefined4 *)(iVar5 + uVar4 * 0x1000 + 0x238) = 0x800000;
          }
          else {
            *(undefined4 *)(iVar5 + uVar4 * 0x1000 + 0x224) = 0;
            param_1[6] = 0;
            FUN_0055c174(param_1);
          }
        }
      }
      iVar5 = 0;
    }
  }
  return iVar5;
}

