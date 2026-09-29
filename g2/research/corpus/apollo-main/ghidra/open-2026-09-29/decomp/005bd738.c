
int FUN_005bd738(undefined4 param_1,int *param_2,undefined4 param_3,undefined4 param_4,int param_5)

{
  int iVar1;
  int iVar2;
  undefined4 local_20;
  
  local_20 = 0;
  iVar1 = (**(code **)(param_5 + 0x20))(*(undefined4 *)(param_5 + 0x28),0x13,4);
  if (iVar1 == 0) {
    iVar2 = -4;
  }
  else {
    iVar2 = FUN_005bd3a0(param_1,0x13,0x13,0,0,param_3,param_2,param_4,&local_20,iVar1);
    if (iVar2 == -3) {
      *(undefined4 *)(param_5 + 0x18) = DAT_005bdf74;
    }
    else if ((iVar2 == -5) || (*param_2 == 0)) {
      *(undefined4 *)(param_5 + 0x18) = DAT_005bdf78;
      iVar2 = -3;
    }
    (**(code **)(param_5 + 0x24))(*(undefined4 *)(param_5 + 0x28),iVar1);
  }
  return iVar2;
}

