
int FUN_004cd7d2(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,int param_5,
                undefined4 *param_6,uint *param_7)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  undefined1 auStack_38 [4];
  undefined4 local_34;
  uint local_30;
  undefined4 local_2c;
  undefined4 local_28;
  
  local_28 = param_4;
  do {
    iVar1 = FUN_004cb186(param_1,&local_2c);
    if (iVar1 != 0) {
      return iVar1;
    }
    iVar1 = FUN_004cad2e(param_1,local_2c);
    if (iVar1 == 0) {
      if (param_5 == 0) {
        *param_6 = local_2c;
        *param_7 = 0;
        return 0;
      }
      local_30 = param_5 - 1;
      iVar1 = FUN_004cd6e4(param_1,&local_30);
      local_30 = local_30 + 1;
      if (local_30 == *(uint *)(*(int *)(param_1 + 0x68) + 0x1c)) {
        uVar2 = lfs_ctz(iVar1 + 1);
        local_34 = local_28;
        uVar3 = 0;
        while( true ) {
          if (uVar2 + 1 <= uVar3) {
            *param_6 = local_2c;
            *param_7 = (uVar2 + 1) * 4;
            return 0;
          }
          local_34 = lfs_tole32(local_34);
          iVar1 = FUN_004cac04(param_1,param_2,param_3,1,local_2c,uVar3 << 2,&local_34,4);
          local_34 = lfs_fromle32(local_34);
          if (iVar1 != 0) break;
          if (uVar3 != uVar2) {
            iVar1 = FUN_004ca83c(param_1,0,param_3,4,local_34,uVar3 << 2,&local_34,4);
            local_34 = lfs_fromle32(local_34);
            if (iVar1 != 0) {
              return iVar1;
            }
          }
          uVar3 = uVar3 + 1;
        }
      }
      else {
        uVar2 = 0;
        while( true ) {
          if (local_30 <= uVar2) {
            *param_6 = local_2c;
            *param_7 = local_30;
            return 0;
          }
          iVar1 = FUN_004ca83c(param_1,0,param_3,local_30 - uVar2,local_28,uVar2,auStack_38,1);
          if (iVar1 != 0) {
            return iVar1;
          }
          iVar1 = FUN_004cac04(param_1,param_2,param_3,1,local_2c,uVar2,auStack_38,1);
          if (iVar1 != 0) break;
          uVar2 = uVar2 + 1;
        }
      }
    }
    if (iVar1 != -0x54) {
      return iVar1;
    }
    FUN_004733ee(DAT_004ce3b8,DAT_004ce3b4,0xbc5,local_2c,&DAT_004cd970);
    FUN_004ca81a(param_1,param_2);
  } while( true );
}

