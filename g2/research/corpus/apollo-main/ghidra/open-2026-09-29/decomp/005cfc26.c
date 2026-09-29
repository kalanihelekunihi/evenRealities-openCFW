
int FUN_005cfc26(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 *puVar5;
  int local_50;
  int local_4c;
  undefined4 local_48;
  undefined1 local_44 [4];
  undefined4 local_40;
  undefined1 local_3c;
  undefined4 local_38;
  undefined1 local_34;
  undefined4 local_30;
  undefined1 local_2c;
  undefined4 local_28;
  undefined1 local_24;
  undefined4 local_20;
  undefined4 uStack_1c;
  
  iVar3 = param_1[2];
  iVar4 = -1;
  uStack_1c = param_4;
  iVar1 = FUN_005cfc04(param_1,&local_4c);
  if ((iVar1 == 0) && (-1 < local_4c)) {
    *(int *)(iVar3 + 0x20) = local_4c;
    if (*(int *)(iVar3 + 0x20) != 0) {
      uVar2 = ft_mem_realloc(*param_1,0x14,0,*(undefined4 *)(iVar3 + 0x20),0,&local_50);
      *(undefined4 *)(iVar3 + 0x1c) = uVar2;
      if (local_50 != 0) {
        return local_50;
      }
    }
    do {
      while( true ) {
        iVar1 = FUN_005cfaf4(param_1,1,&local_48);
        if (iVar1 == 0) {
          return 0xa0;
        }
        iVar1 = FUN_005cfb62(iVar1,local_48);
        if (((iVar1 == 0x14) || (iVar1 == 0x15)) || (iVar1 == 0x17)) {
          *(int *)(iVar3 + 0x20) = iVar4 + 1;
          return 0;
        }
        if (iVar1 != 0x38) break;
        iVar4 = iVar4 + 1;
        if (*(int *)(iVar3 + 0x20) <= iVar4) {
          return 0xa0;
        }
        puVar5 = (undefined4 *)(*(int *)(iVar3 + 0x1c) + iVar4 * 0x14);
        local_44[0] = 3;
        local_3c = 2;
        local_34 = 2;
        local_2c = 2;
        local_24 = 2;
        iVar1 = FUN_005cf9e8(param_1,local_44,5);
        if (iVar1 != 5) {
          return 0xa0;
        }
        *puVar5 = local_40;
        puVar5[1] = local_38;
        puVar5[2] = local_30;
        puVar5[3] = local_28;
        puVar5[4] = local_20;
      }
    } while (iVar1 == 0x4b);
  }
  return 0xa0;
}

