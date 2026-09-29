
int FUN_005cfd38(undefined4 *param_1)

{
  byte bVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  undefined4 *puVar7;
  int local_48;
  int local_44;
  undefined4 local_40;
  undefined1 local_3c [4];
  undefined4 local_38;
  undefined1 local_34;
  undefined4 local_30;
  undefined1 local_2c;
  undefined4 local_28;
  undefined1 local_24;
  undefined4 local_20;
  
  iVar5 = param_1[2];
  iVar6 = -1;
  iVar2 = FUN_005cfc04(param_1,&local_44);
  if ((iVar2 == 0) && (-1 < local_44)) {
    *(int *)(iVar5 + 0x28) = local_44;
    if (*(int *)(iVar5 + 0x28) != 0) {
      uVar3 = ft_mem_realloc(*param_1,0x10,0,*(undefined4 *)(iVar5 + 0x28),0,&local_48);
      *(undefined4 *)(iVar5 + 0x24) = uVar3;
      if (local_48 != 0) {
        return local_48;
      }
    }
    do {
      while( true ) {
        iVar2 = FUN_005cfaf4(param_1,1,&local_40);
        if (iVar2 == 0) {
          return 0xa0;
        }
        bVar1 = FUN_005cfb62(iVar2,local_40);
        uVar4 = (uint)bVar1;
        if (uVar4 - 0x14 < 3) {
          *(int *)(iVar5 + 0x28) = iVar6 + 1;
          FUN_00567c4c(*(undefined4 *)(iVar5 + 0x24),*(undefined4 *)(iVar5 + 0x28),0x10,DAT_005d0704
                      );
          return 0;
        }
        if ((uVar4 != 0x22) && (1 < uVar4 - 0x24)) break;
        iVar6 = iVar6 + 1;
        if (*(int *)(iVar5 + 0x28) <= iVar6) {
          return 0xa0;
        }
        puVar7 = (undefined4 *)(*(int *)(iVar5 + 0x24) + iVar6 * 0x10);
        local_3c[0] = 5;
        local_34 = 5;
        local_2c = 3;
        local_24 = 3;
        iVar2 = FUN_005cf9e8(param_1,local_3c,4);
        if (iVar2 < 3) {
          return 0xa0;
        }
        *puVar7 = local_38;
        puVar7[1] = local_30;
        if (bVar1 == 0x25) {
          puVar7[2] = 0;
          puVar7[3] = local_28;
        }
        else {
          puVar7[2] = local_28;
          if ((bVar1 != 0x22) || (uVar3 = local_20, iVar2 != 4)) {
            uVar3 = 0;
          }
          puVar7[3] = uVar3;
        }
      }
    } while (uVar4 - 0x24 == 0x27);
  }
  return 0xa0;
}

