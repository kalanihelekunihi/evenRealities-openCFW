
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_004fec14(undefined1 param_1,int param_2,int *param_3,undefined4 param_4)

{
  undefined1 *puVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 auStack_40 [12];
  int iStack_34;
  undefined1 auStack_2c [20];
  undefined4 uStack_18;
  
  puVar1 = DAT_004fec84;
  if (((param_2 == 0) || (param_3 == (int *)0x0)) || (*param_3 == 0)) {
    uVar2 = 0;
  }
  else {
    uStack_18 = param_4;
    FUN_004fdd6e(DAT_004fec84);
    *puVar1 = 1;
    *(undefined4 *)(puVar1 + 4) = *_DAT_004feef8;
    *(undefined2 *)(puVar1 + 8) = 3;
    *(undefined4 *)(puVar1 + 0x10) = *_DAT_004ff1e8;
    puVar1[0x14] = param_1;
    FUN_004905f4(auStack_2c,param_2,*param_3);
    FUN_00439c04(auStack_40,auStack_2c,0x14);
    iVar3 = FUN_00490c32(auStack_40,DAT_004fec88,puVar1);
    if (iVar3 == 0) {
      uVar2 = 0;
    }
    else {
      *param_3 = iStack_34;
      uVar2 = 1;
    }
  }
  return uVar2;
}

