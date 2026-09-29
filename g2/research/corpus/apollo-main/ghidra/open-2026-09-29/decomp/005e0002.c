
undefined8 FUN_005e0002(int param_1,undefined4 param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  int local_18;
  
  iVar2 = *(int *)(param_1 + 0x68);
  local_18 = param_4;
  iVar1 = (**(code **)(param_1 + 0x204))(param_1,s_tsopX_t_005e04c4._0_4_,iVar2,&local_18);
  if (iVar1 == 0) {
    iVar4 = local_18 + *(int *)(iVar2 + 8);
    iVar3 = *(int *)(param_1 + 0x1dc);
    iVar1 = FT_Stream_Skip(iVar2,0x20);
    if (iVar1 == 0) {
      if (iVar3 == 0x20000) {
        iVar1 = FUN_005dfd20(param_1,iVar2,iVar4);
      }
      else if (iVar3 == 0x25000) {
        iVar1 = FUN_005dff5a(param_1,iVar2,iVar4);
      }
      else {
        iVar1 = 3;
      }
      *(undefined1 *)(param_1 + 0x278) = 1;
    }
  }
  return CONCAT44(local_18,iVar1);
}

