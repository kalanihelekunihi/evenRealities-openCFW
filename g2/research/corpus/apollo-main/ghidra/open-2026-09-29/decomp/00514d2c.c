
/* WARNING: Removing unreachable block (ram,0x00514d50) */

undefined4 FUN_00514d2c(int param_1)

{
  undefined4 uVar1;
  int iVar2;
  
  iVar2 = *(int *)(*DAT_00514d94 + 4);
  if (iVar2 == 0) {
    FUN_004b127c(0x80);
    return 0xfffffffe;
  }
  if ((-1 < *(int *)(iVar2 + 0x18) << 0x1a) &&
     ((*(int *)(iVar2 + 0x10) - *(int *)(iVar2 + 0x14)) / 2 <= param_1)) {
    if (*(int *)(iVar2 + 0x18) << 0x1e < 0) {
      iVar2 = FUN_00514504();
      if (-1 < iVar2) {
        return 0;
      }
      uVar1 = 0x10;
    }
    else {
      uVar1 = 8;
    }
    FUN_004b127c(uVar1);
    return 0xffffffff;
  }
  return 0;
}

