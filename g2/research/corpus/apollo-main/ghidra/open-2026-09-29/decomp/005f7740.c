
undefined4 Ins_DELTAC(int param_1,uint *param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  
  iVar2 = (**(code **)(param_1 + 0x254))(param_1);
  uVar7 = *param_2;
  uVar8 = 1;
  do {
    if (uVar7 < uVar8) {
LAB_005f77ca:
      *(undefined4 *)(param_1 + 0x20) = *(undefined4 *)(param_1 + 0x1c);
      return param_4;
    }
    if (*(int *)(param_1 + 0x1c) < 2) {
      if (*(char *)(param_1 + 0x235) != '\0') {
        *(undefined4 *)(param_1 + 0xc) = 0x81;
      }
      *(undefined4 *)(param_1 + 0x1c) = 0;
      goto LAB_005f77ca;
    }
    *(int *)(param_1 + 0x1c) = *(int *)(param_1 + 0x1c) + -2;
    uVar4 = *(uint *)(*(int *)(param_1 + 0x18) + *(int *)(param_1 + 0x1c) * 4 + 4);
    uVar6 = *(uint *)(*(int *)(param_1 + 0x18) + *(int *)(param_1 + 0x1c) * 4);
    if (uVar4 < *(uint *)(param_1 + 0x180)) {
      uVar3 = (uVar6 & 0xff) >> 4;
      bVar1 = *(byte *)(param_1 + 0x174);
      if ((bVar1 != 0x73) && (0x72 < bVar1)) {
        if (bVar1 == 0x75) {
          uVar3 = uVar3 + 0x20;
        }
        else if (bVar1 < 0x75) {
          uVar3 = uVar3 + 0x10;
        }
      }
      if (iVar2 == uVar3 + *(ushort *)(param_1 + 0x150)) {
        uVar6 = uVar6 & 0xf;
        iVar5 = uVar6 - 8;
        if (-1 < iVar5) {
          iVar5 = uVar6 - 7;
        }
        (**(code **)(param_1 + 0x260))
                  (param_1,uVar4,(1 << (6 - *(ushort *)(param_1 + 0x152) & 0xff)) * iVar5);
      }
    }
    else if (*(char *)(param_1 + 0x235) != '\0') {
      *(undefined4 *)(param_1 + 0xc) = 0x86;
      return param_4;
    }
    uVar8 = uVar8 + 1;
  } while( true );
}

