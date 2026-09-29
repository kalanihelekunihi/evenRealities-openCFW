
int FUN_00414954(int param_1,code *param_2,undefined4 param_3,char param_4)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;
  ushort uVar4;
  undefined4 local_54 [2];
  undefined1 auStack_4c [20];
  ushort local_38;
  undefined4 local_34 [2];
  undefined1 auStack_2c [16];
  
  FUN_004156ac(auStack_4c,DAT_0041526c,0x20);
  FUN_004156ac(auStack_2c,DAT_00415270,0x10);
  while (iVar1 = FUN_00410ad8(local_34), iVar1 == 0) {
    iVar1 = FUN_004145fc(auStack_4c,auStack_2c);
    if (iVar1 < 0) {
      return -0x54;
    }
    for (iVar1 = 0; iVar1 < 2; iVar1 = iVar1 + 1) {
      iVar2 = (*param_2)(param_3,local_34[iVar1]);
      if (iVar2 != 0) {
        return iVar2;
      }
    }
    iVar1 = FUN_00411be4(param_1,auStack_4c,local_34);
    if (iVar1 != 0) {
      return iVar1;
    }
    for (uVar4 = 0; uVar4 < local_38; uVar4 = uVar4 + 1) {
      iVar1 = FUN_004110d0(param_1,auStack_4c,DAT_004152c0,DAT_004152bc | (uint)uVar4 << 10,local_54
                          );
      if (iVar1 < 0) {
        if (iVar1 != -2) {
          return iVar1;
        }
      }
      else {
        FUN_00410cf2(local_54);
        iVar2 = lfs_tag_type3(iVar1);
        if (iVar2 == 0x202) {
          iVar1 = FUN_004134c4(param_1,0,param_1,local_54[0],local_54[1],param_2,param_3);
          if (iVar1 != 0) {
            return iVar1;
          }
        }
        else if ((param_4 != '\0') && (iVar1 = lfs_tag_type3(iVar1), iVar1 == 0x200)) {
          for (iVar1 = 0; iVar1 < 2; iVar1 = iVar1 + 1) {
            iVar2 = (*param_2)(param_3,local_54[iVar1]);
            if (iVar2 != 0) {
              return iVar2;
            }
          }
        }
      }
    }
  }
  puVar3 = *(undefined4 **)(param_1 + 0x28);
  do {
    if (puVar3 == (undefined4 *)0x0) {
      return 0;
    }
    if (*(char *)((int)puVar3 + 6) == '\x01') {
      if (((puVar3[0xc] & 0x110000) == 0x10000) &&
         (iVar1 = FUN_004134c4(param_1,puVar3 + 0x10,param_1,puVar3[10],puVar3[0xb],param_2,param_3)
         , iVar1 != 0)) {
        return iVar1;
      }
      if (((puVar3[0xc] & 0x120000) == 0x20000) &&
         (iVar1 = FUN_004134c4(param_1,puVar3 + 0x10,param_1,puVar3[0xe],puVar3[0xd],param_2,param_3
                              ), iVar1 != 0)) {
        return iVar1;
      }
    }
    puVar3 = (undefined4 *)*puVar3;
  } while( true );
}

