
int FUN_005cfefa(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined1 *puVar3;
  undefined4 uVar4;
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
  undefined4 uStack_1c;
  
  uVar4 = *param_1;
  puVar3 = (undefined1 *)param_1[2];
  iVar2 = 0xa0;
  local_48 = 0;
  if (puVar3 == (undefined1 *)0x0) {
    iVar2 = 6;
  }
  else {
    uStack_1c = param_4;
    iVar1 = FUN_005cfaf4(param_1,1,&local_44);
    if (((iVar1 != 0) && (local_44 == 0x10)) &&
       (iVar1 = FUN_0044b610(iVar1,DAT_005d0708,0x10), iVar1 == 0)) {
      do {
        while( true ) {
          while( true ) {
            while( true ) {
              while( true ) {
                while( true ) {
                  while( true ) {
                    iVar1 = FUN_005cfaf4(param_1,1,&local_44);
                    if (iVar1 == 0) goto LAB_005cff8e;
                    iVar1 = FUN_005cfb62(iVar1,local_44);
                    if (iVar1 != 0) break;
                    local_3c[0] = 2;
                    iVar1 = FUN_005cf9e8(param_1,local_3c,1);
                    if (iVar1 != 1) goto LAB_005cff8e;
                    *(undefined4 *)(puVar3 + 0x14) = local_38;
                  }
                  if (iVar1 != 0xe) break;
                  local_3c[0] = 2;
                  iVar1 = FUN_005cf9e8(param_1,local_3c,1);
                  if (iVar1 != 1) goto LAB_005cff8e;
                  *(undefined4 *)(puVar3 + 0x18) = local_38;
                }
                if (iVar1 == 0x14) {
                  return 0;
                }
                if (iVar1 != 0x1a) break;
                local_3c[0] = 2;
                local_34 = 2;
                local_2c = 2;
                local_24 = 2;
                iVar1 = FUN_005cf9e8(param_1,local_3c,4);
                if (iVar1 != 4) goto LAB_005cff8e;
                *(undefined4 *)(puVar3 + 4) = local_38;
                *(undefined4 *)(puVar3 + 8) = local_30;
                *(undefined4 *)(puVar3 + 0xc) = local_28;
                *(undefined4 *)(puVar3 + 0x10) = local_20;
              }
              if (iVar1 != 0x1e) break;
              local_3c[0] = 4;
              iVar1 = FUN_005cf9e8(param_1,local_3c,1);
              if (iVar1 != 1) goto LAB_005cff8e;
              *puVar3 = (undefined1)local_38;
            }
            if (iVar1 != 0x28) break;
            iVar1 = FUN_005cfc04(param_1,&local_48);
            if (iVar1 != 0) goto LAB_005cff8e;
            if ((local_48 != 0) && (local_48 != 2)) {
              iVar2 = 7;
              goto LAB_005cff8e;
            }
          }
          if (iVar1 != 0x2d) break;
          local_40 = 0;
          iVar1 = FUN_005cfc04(param_1,&local_40);
          if (iVar1 != 0) goto LAB_005cff8e;
          iVar2 = FUN_005cfeaa(param_1,local_40,0x11);
          if (iVar2 != 0) {
            return iVar2;
          }
        }
      } while (iVar1 != 0x31);
      iVar2 = FUN_005cfe54(param_1);
      if (iVar2 == 0) {
        return 0;
      }
LAB_005cff8e:
      ft_mem_free(uVar4,*(undefined4 *)(puVar3 + 0x1c));
      *(undefined4 *)(puVar3 + 0x1c) = 0;
      *(undefined4 *)(puVar3 + 0x20) = 0;
      ft_mem_free(uVar4,*(undefined4 *)(puVar3 + 0x24));
      *(undefined4 *)(puVar3 + 0x24) = 0;
      *(undefined4 *)(puVar3 + 0x28) = 0;
      *puVar3 = 0;
      return iVar2;
    }
    iVar2 = 2;
  }
  return iVar2;
}

