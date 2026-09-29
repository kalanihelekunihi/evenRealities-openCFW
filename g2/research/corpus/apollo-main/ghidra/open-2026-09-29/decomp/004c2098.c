
undefined8 FUN_004c2098(uint *param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 uVar4;
  uint uVar5;
  undefined4 uVar6;
  
  iVar2 = 0;
  uVar6 = param_3;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004c2adc)) {
    iVar2 = 2;
  }
  else if (((*(char *)((int)param_1 + 10) == '\n') || (*(char *)((int)param_1 + 10) == '\v')) &&
          ((*(byte *)(param_2 + 2) & 3) != 0)) {
    iVar2 = 7;
  }
  else if (*(char *)((int)param_2 + 0x12) == '\0') {
    uVar3 = param_1[1];
    if ((param_1[8] == 0) && (param_1[0x210] == 0)) {
      if ((char)param_1[0x20b] == '\x02') {
        iVar2 = 7;
      }
      else {
        uVar5 = (*(byte *)((int)param_2 + 6) & 1) << 7 |
                *param_2 << 0x10 | (uint)*(byte *)(param_2 + 1) << 9;
        if ((char)param_2[3] != '\0') {
          uVar5 = uVar5 | 0x40;
          *(uint *)(DAT_004c26dc + uVar3 * 0x1000 + 0xc) = (uint)*(ushort *)((int)param_2 + 0xe);
        }
        if (*(char *)((int)param_2 + 7) != '\0') {
          uVar5 = uVar5 | 0x20;
          *(int *)(DAT_004c26dc + uVar3 * 0x1000 + 8) = param_2[2];
        }
        iVar1 = DAT_004c26dc;
        if ((char)param_2[4] != '\0') {
          uVar5 = uVar5 | 0x400;
        }
        uVar5 = uVar5 | (uint)*(byte *)((int)param_1 + 0xd) << 8 |
                (uint)*(byte *)((int)param_2 + 0x11) << 0xc;
        if (*(char *)((int)param_2 + 5) != '\0') {
          uVar5 = uVar5 | 0x800;
        }
        uVar4 = *(undefined4 *)(DAT_004c26dc + uVar3 * 0x1000 + 0x200);
        *(undefined4 *)(DAT_004c26dc + uVar3 * 0x1000 + 0x200) = 0;
        *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x208) = 0xffffffff;
        *(uint *)(iVar1 + uVar3 * 0x1000) = uVar5 | 1;
        if (*(char *)((int)param_2 + 6) == '\0') {
          iVar2 = FUN_004bfbbc(uVar3,param_2[5],*param_2,param_1[4]);
        }
        else if (*(char *)((int)param_2 + 6) == '\x01') {
          iVar2 = FUN_004bfb72(uVar3,param_2[5],*param_2,param_1[4],param_3,param_4);
        }
        if (iVar2 == 0) {
          uVar6 = 1;
          iVar2 = FUN_00480826(param_3,iVar1 + uVar3 * 0x1000,2,2);
          *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x208) = 0xffffffff;
          *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x200) = uVar4;
        }
        else {
          *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x208) = 0xffffffff;
          *(undefined4 *)(iVar1 + uVar3 * 0x1000 + 0x200) = uVar4;
        }
      }
    }
    else {
      iVar2 = 7;
    }
  }
  else {
    iVar2 = 7;
  }
  return CONCAT44(uVar6,iVar2);
}

