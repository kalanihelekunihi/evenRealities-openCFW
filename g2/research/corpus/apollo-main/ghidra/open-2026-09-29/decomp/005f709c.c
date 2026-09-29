
undefined8 Ins_IP(int param_1,int *param_2,undefined4 param_3)

{
  bool bVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int *piVar6;
  undefined4 uVar7;
  uint uVar8;
  int *local_30;
  undefined4 local_2c;
  
  local_30 = param_2;
  local_2c = param_3;
  if (*(int *)(param_1 + 0x10) < *(int *)(param_1 + 0x134)) {
    if (*(char *)(param_1 + 0x235) != '\0') {
      *(undefined4 *)(param_1 + 0xc) = 0x86;
    }
  }
  else {
    if (((*(short *)(param_1 + 0x15c) == 0) || (*(short *)(param_1 + 0x15e) == 0)) ||
       (*(short *)(param_1 + 0x160) == 0)) {
      bVar1 = true;
    }
    else {
      bVar1 = false;
    }
    if (*(ushort *)(param_1 + 0x122) < *(ushort *)(param_1 + 0x2c)) {
      if (bVar1) {
        piVar6 = (int *)(*(int *)(param_1 + 0x30) + (uint)*(ushort *)(param_1 + 0x122) * 8);
      }
      else {
        piVar6 = (int *)(*(int *)(param_1 + 0x38) + (uint)*(ushort *)(param_1 + 0x122) * 8);
      }
      local_30 = (int *)(*(int *)(param_1 + 0x34) + (uint)*(ushort *)(param_1 + 0x122) * 8);
      if ((*(ushort *)(param_1 + 0x122) < *(ushort *)(param_1 + 0x2c)) &&
         (*(ushort *)(param_1 + 0x124) < *(ushort *)(param_1 + 0x50))) {
        if (bVar1) {
          iVar5 = (**(code **)(param_1 + 0x244))
                            (param_1,*(int *)(*(int *)(param_1 + 0x54) +
                                             (uint)*(ushort *)(param_1 + 0x124) * 8) - *piVar6,
                             *(int *)(*(int *)(param_1 + 0x54) +
                                      (uint)*(ushort *)(param_1 + 0x124) * 8 + 4) - piVar6[1]);
        }
        else if (*(int *)(param_1 + 0xe0) == *(int *)(param_1 + 0xe4)) {
          iVar5 = (**(code **)(param_1 + 0x244))
                            (param_1,*(int *)(*(int *)(param_1 + 0x5c) +
                                             (uint)*(ushort *)(param_1 + 0x124) * 8) - *piVar6,
                             *(int *)(*(int *)(param_1 + 0x5c) +
                                      (uint)*(ushort *)(param_1 + 0x124) * 8 + 4) - piVar6[1]);
        }
        else {
          local_2c = FT_MulFix(*(int *)(*(int *)(param_1 + 0x5c) +
                                       (uint)*(ushort *)(param_1 + 0x124) * 8) - *piVar6,
                               *(undefined4 *)(param_1 + 0xe0));
          uVar7 = FT_MulFix(*(int *)(*(int *)(param_1 + 0x5c) +
                                     (uint)*(ushort *)(param_1 + 0x124) * 8 + 4) - piVar6[1],
                            *(undefined4 *)(param_1 + 0xe4));
          iVar5 = (**(code **)(param_1 + 0x244))(param_1,local_2c,uVar7);
        }
        uVar7 = (**(code **)(param_1 + 0x240))
                          (param_1,*(int *)(*(int *)(param_1 + 0x58) +
                                           (uint)*(ushort *)(param_1 + 0x124) * 8) - *local_30,
                           *(int *)(*(int *)(param_1 + 0x58) +
                                    (uint)*(ushort *)(param_1 + 0x124) * 8 + 4) - local_30[1]);
      }
      else {
        iVar5 = 0;
        uVar7 = 0;
      }
      while (0 < *(int *)(param_1 + 0x134)) {
        *(int *)(param_1 + 0x1c) = *(int *)(param_1 + 0x1c) + -1;
        uVar8 = *(uint *)(*(int *)(param_1 + 0x18) + *(int *)(param_1 + 0x1c) * 4);
        if (uVar8 < *(ushort *)(param_1 + 0x74)) {
          if (bVar1) {
            iVar2 = (**(code **)(param_1 + 0x244))
                              (param_1,*(int *)(*(int *)(param_1 + 0x78) + uVar8 * 8) - *piVar6,
                               *(int *)(*(int *)(param_1 + 0x78) + uVar8 * 8 + 4) - piVar6[1]);
          }
          else if (*(int *)(param_1 + 0xe0) == *(int *)(param_1 + 0xe4)) {
            iVar2 = (**(code **)(param_1 + 0x244))
                              (param_1,*(int *)(*(int *)(param_1 + 0x80) + uVar8 * 8) - *piVar6,
                               *(int *)(*(int *)(param_1 + 0x80) + uVar8 * 8 + 4) - piVar6[1]);
          }
          else {
            local_2c = FT_MulFix(*(int *)(*(int *)(param_1 + 0x80) + uVar8 * 8) - *piVar6,
                                 *(undefined4 *)(param_1 + 0xe0));
            uVar3 = FT_MulFix(*(int *)(*(int *)(param_1 + 0x80) + uVar8 * 8 + 4) - piVar6[1],
                              *(undefined4 *)(param_1 + 0xe4));
            iVar2 = (**(code **)(param_1 + 0x244))(param_1,local_2c,uVar3);
          }
          iVar4 = (**(code **)(param_1 + 0x240))
                            (param_1,*(int *)(*(int *)(param_1 + 0x7c) + uVar8 * 8) - *local_30,
                             *(int *)(*(int *)(param_1 + 0x7c) + uVar8 * 8 + 4) - local_30[1]);
          if (iVar2 == 0) {
            iVar2 = 0;
          }
          else if (iVar5 != 0) {
            iVar2 = FT_MulDiv(iVar2,uVar7,iVar5);
          }
          (**(code **)(param_1 + 0x24c))(param_1,param_1 + 0x6c,uVar8 & 0xffff,iVar2 - iVar4);
        }
        else if (*(char *)(param_1 + 0x235) != '\0') {
          *(undefined4 *)(param_1 + 0xc) = 0x86;
          goto LAB_005f70c2;
        }
        *(int *)(param_1 + 0x134) = *(int *)(param_1 + 0x134) + -1;
      }
    }
    else if (*(char *)(param_1 + 0x235) != '\0') {
      *(undefined4 *)(param_1 + 0xc) = 0x86;
    }
  }
  *(undefined4 *)(param_1 + 0x134) = 1;
  *(undefined4 *)(param_1 + 0x20) = *(undefined4 *)(param_1 + 0x1c);
LAB_005f70c2:
  return CONCAT44(local_2c,local_30);
}

