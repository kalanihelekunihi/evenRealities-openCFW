
undefined8
FT_Raccess_Guess(undefined4 param_1,int param_2,int param_3,int param_4,int param_5,int param_6)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 local_28;
  
  local_28 = param_3;
  for (iVar2 = 0; iVar2 < 9; iVar2 = iVar2 + 1) {
    *(undefined4 *)(param_4 + iVar2 * 4) = 0;
    if (param_2 == 0) {
      *(undefined4 *)(param_6 + iVar2 * 4) = 0;
    }
    else {
      uVar1 = FT_Stream_Seek(param_2,0);
      *(undefined4 *)(param_6 + iVar2 * 4) = uVar1;
    }
    if (*(int *)(param_6 + iVar2 * 4) == 0) {
      local_28 = param_5 + iVar2 * 4;
      uVar1 = (**(code **)(DAT_00528714 + iVar2 * 8))(param_1,param_2,param_3,param_4 + iVar2 * 4);
      *(undefined4 *)(param_6 + iVar2 * 4) = uVar1;
    }
  }
  return CONCAT44(param_4,local_28);
}

