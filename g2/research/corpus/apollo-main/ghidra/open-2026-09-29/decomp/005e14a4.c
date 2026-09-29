
int FUN_005e14a4(int param_1,undefined4 param_2,undefined4 param_3,uint param_4,undefined4 param_5,
                int param_6,uint param_7)

{
  uint uVar1;
  int iVar2;
  undefined4 uVar3;
  int local_60;
  uint local_5c;
  uint local_58;
  undefined4 local_54;
  undefined2 local_50;
  undefined1 local_4e;
  undefined1 auStack_48 [44];
  uint uStack_1c;
  
  uVar1 = *(byte *)(param_1 + 0x2f8) - 1;
  uStack_1c = param_4;
  if (uVar1 < 2) {
    iVar2 = FUN_005e072a(auStack_48,param_1,param_2);
    if (iVar2 == 0) {
      local_5c = param_4 >> 0x16 & 1;
      local_60 = 0;
      iVar2 = FUN_005e0eb4(auStack_48,param_3,0,0);
      FUN_005e0816(auStack_48);
    }
  }
  else if (uVar1 == 2) {
    local_58 = param_4 >> 0x16 & 1;
    local_5c = param_7;
    local_60 = param_6;
    iVar2 = FUN_005e12c8(param_1,param_2,param_3,param_5);
  }
  else {
    iVar2 = 2;
  }
  if (((iVar2 == 0) && ((param_4 & 0x500000) == 0)) && (*(char *)(param_6 + 0x12) == '\a')) {
    uVar3 = **(undefined4 **)(param_1 + 0x54);
    FUN_0058ed20(&local_60);
    iVar2 = FUN_0058ee9e(uVar3,param_6,&local_60,1);
    if (iVar2 == 0) {
      *(undefined1 *)(param_6 + 0x12) = local_4e;
      *(uint *)(param_6 + 8) = local_58;
      *(undefined2 *)(param_6 + 0x10) = local_50;
      ft_glyphslot_set_bitmap(*(undefined4 *)(param_1 + 0x54),local_54);
      *(uint *)(*(int *)(*(int *)(param_1 + 0x54) + 0x9c) + 4) =
           *(uint *)(*(int *)(*(int *)(param_1 + 0x54) + 0x9c) + 4) | 1;
    }
    else {
      FUN_0058f156(uVar3,&local_60);
    }
  }
  return iVar2;
}

