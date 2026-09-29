
undefined4 Ins_DELTAP(int *param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  
  iVar2 = (*(code *)param_1[0x95])(param_1);
  uVar7 = *param_2;
  uVar8 = 1;
  do {
    if (uVar7 < uVar8) {
LAB_005f7720:
      param_1[8] = param_1[7];
      return param_4;
    }
    if (param_1[7] < 2) {
      if (*(char *)((int)param_1 + 0x235) != '\0') {
        param_1[3] = 0x81;
      }
      param_1[7] = 0;
      goto LAB_005f7720;
    }
    param_1[7] = param_1[7] + -2;
    uVar4 = *(uint *)(param_1[6] + param_1[7] * 4 + 4);
    uVar5 = *(uint *)(param_1[6] + param_1[7] * 4);
    if ((uVar4 & 0xffff) < (uint)*(ushort *)(param_1 + 0xb)) {
      uVar3 = (uVar5 & 0xff) >> 4;
      cVar1 = (char)param_1[0x5d];
      if (cVar1 != ']') {
        if (cVar1 == 'q') {
          uVar3 = uVar3 + 0x10;
        }
        else if (cVar1 == 'r') {
          uVar3 = uVar3 + 0x20;
        }
      }
      if (iVar2 == uVar3 + *(ushort *)(param_1 + 0x54)) {
        uVar5 = uVar5 & 0xf;
        iVar6 = uVar5 - 8;
        if (-1 < iVar6) {
          iVar6 = uVar5 - 7;
        }
        if ((*(int *)(*(int *)(*param_1 + 0x60) + 0x40) == 0x28) &&
           (*(char *)((int)param_1 + 0x267) != '\0')) {
          if ((((char)param_1[0x9a] == '\0') || (*(char *)((int)param_1 + 0x269) == '\0')) &&
             ((((char)param_1[0x8d] != '\0' && ((short)param_1[0x4c] != 0)) ||
              ((int)((uint)*(byte *)(param_1[0xf] + (uVar4 & 0xffff)) << 0x1b) < 0)))) {
            (*(code *)param_1[0x93])(param_1,param_1 + 9,uVar4 & 0xffff);
          }
        }
        else {
          (*(code *)param_1[0x93])
                    (param_1,param_1 + 9,uVar4 & 0xffff,
                     (1 << (6 - *(ushort *)((int)param_1 + 0x152) & 0xff)) * iVar6);
        }
      }
    }
    else if (*(char *)((int)param_1 + 0x235) != '\0') {
      param_1[3] = 0x86;
    }
    uVar8 = uVar8 + 1;
  } while( true );
}

