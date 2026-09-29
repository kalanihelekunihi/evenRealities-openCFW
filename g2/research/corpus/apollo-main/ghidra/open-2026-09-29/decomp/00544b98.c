
undefined4 FUN_00544b98(char *param_1,undefined4 *param_2)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  undefined1 auStack_88 [4];
  undefined1 auStack_84 [16];
  uint local_74;
  char local_6c;
  char local_6b;
  undefined1 local_6a;
  undefined1 auStack_5c [64];
  int local_1c;
  
  puVar3 = (undefined4 *)*param_2;
  if ((*param_1 != '\0') && ((param_1[2] == '\x02' || (param_1[2] == '\x03')))) {
    FUN_005858d8(puVar3,*(int *)(param_1 + 4) + 1,auStack_88,4,3,1);
    local_1c = *(int *)(param_1 + 4) + 0x10;
    do {
      FUN_00544000(puVar3,&local_6c);
      if ((local_6b != '\0') &&
         (((local_6c == '\x02' || (local_6c == '\x03')) &&
          (iVar1 = FUN_005449c0(puVar3,&local_6c), iVar1 != 0)))) {
        FUN_004733ee(DAT_00545534);
        uVar2 = FUN_00585c94(puVar3);
        FUN_004733ee(DAT_00545538,*puVar3,uVar2);
        FUN_004733ee(DAT_0054553c,local_6a,auStack_5c);
      }
      local_1c = FUN_00543f8c(puVar3,param_1,&local_6c);
    } while (local_1c != -1);
    FUN_005445f2(puVar3,*(undefined4 *)(param_1 + 4),0xffffffff);
    uVar4 = param_2[2];
    param_2[2] = *(undefined4 *)(param_1 + 4);
    uVar2 = FUN_00544374(puVar3,param_1,0);
    puVar3[5] = uVar2;
    iVar1 = FUN_0054418e(puVar3,uVar4,auStack_84,1);
    if ((iVar1 == 0) && ((uint)param_2[1] < local_74)) {
      return 1;
    }
  }
  return 0;
}

