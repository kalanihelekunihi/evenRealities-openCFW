
void FUN_00568d2a(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int local_28;
  int local_24;
  int local_20;
  int local_1c;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  FT_Vector_From_Polar(&local_20,*(undefined4 *)(param_1 + 0x30),(int)&DAT_005a0000 + param_2);
  local_28 = local_20 + *(int *)(param_1 + 8);
  local_24 = local_1c + *(int *)(param_1 + 0xc);
  iVar1 = FUN_00568636(param_1 + 0x34,&local_28);
  if (iVar1 == 0) {
    local_28 = *(int *)(param_1 + 8) - local_20;
    local_24 = *(int *)(param_1 + 0xc) - local_1c;
    FUN_00568636(param_1 + 0x54,&local_28);
    *(int *)(param_1 + 0x18) = param_2;
    *(undefined1 *)(param_1 + 0x14) = 0;
    *(undefined4 *)(param_1 + 0x24) = param_3;
  }
  return;
}

