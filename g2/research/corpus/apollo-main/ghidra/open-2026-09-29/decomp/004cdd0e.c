
int FUN_004cdd0e(int param_1,int param_2)

{
  int iVar1;
  uint uVar2;
  undefined1 auStack_18 [4];
  undefined4 local_14;
  
  do {
    iVar1 = FUN_004cb186(param_1,&local_14);
    if (iVar1 != 0) {
      return iVar1;
    }
    iVar1 = FUN_004cad2e(param_1,local_14);
    if (iVar1 == 0) {
      uVar2 = 0;
      while( true ) {
        if (*(uint *)(param_2 + 0x3c) <= uVar2) {
          FUN_00439be4(*(undefined4 *)(param_2 + 0x4c),*(undefined4 *)(param_1 + 0x1c),
                       *(undefined4 *)(*(int *)(param_1 + 0x68) + 0x28));
          *(undefined4 *)(param_2 + 0x40) = *(undefined4 *)(param_1 + 0x10);
          *(undefined4 *)(param_2 + 0x44) = *(undefined4 *)(param_1 + 0x14);
          *(undefined4 *)(param_2 + 0x48) = *(undefined4 *)(param_1 + 0x18);
          FUN_004ca822(param_1,param_1 + 0x10);
          *(undefined4 *)(param_2 + 0x38) = local_14;
          *(uint *)(param_2 + 0x30) = *(uint *)(param_2 + 0x30) | 0x20000;
          return 0;
        }
        if (*(int *)(param_2 + 0x30) << 0xb < 0) {
          iVar1 = FUN_004cb3f0(param_1,param_2 + 8,0,param_2 + 0x40,*(int *)(param_2 + 0x3c) - uVar2
                               ,DAT_004ce904,DAT_004ce604 | (uint)*(ushort *)(param_2 + 4) << 10,
                               uVar2,auStack_18,1);
        }
        else {
          iVar1 = FUN_004ca83c(param_1,param_2 + 0x40,param_1,*(int *)(param_2 + 0x3c) - uVar2,
                               *(undefined4 *)(param_2 + 0x38),uVar2,auStack_18,1);
        }
        if (iVar1 != 0) {
          return iVar1;
        }
        iVar1 = FUN_004cac04(param_1,param_1 + 0x10,param_1,1,local_14,uVar2,auStack_18,1);
        if (iVar1 != 0) break;
        uVar2 = uVar2 + 1;
      }
    }
    if (iVar1 != -0x54) {
      return iVar1;
    }
    FUN_004733ee(DAT_004ce3b8,DAT_004ce3b4,0xd01,local_14,&DAT_004cdf60);
    FUN_004ca81a(param_1,param_1 + 0x10);
  } while( true );
}

