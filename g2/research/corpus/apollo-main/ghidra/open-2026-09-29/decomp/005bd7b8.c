
int FUN_005bd7b8(uint param_1,undefined4 param_2,int param_3,int *param_4,int *param_5,
                undefined4 param_6,undefined4 param_7,undefined4 param_8,int param_9)

{
  int iVar1;
  int iVar2;
  undefined4 local_28;
  
  local_28 = 0;
  iVar1 = (**(code **)(param_9 + 0x20))(*(undefined4 *)(param_9 + 0x28),0x120,4);
  if (iVar1 == 0) {
    iVar2 = -4;
  }
  else {
    iVar2 = FUN_005bd3a0(param_3,param_1,0x101,DAT_005bdf80,DAT_005bdf7c,param_6,param_4,param_8,
                         &local_28,iVar1);
    if ((iVar2 == 0) && (*param_4 != 0)) {
      iVar2 = FUN_005bd3a0(param_3 + param_1 * 4,param_2,0,DAT_005bdf90,DAT_005bdf8c,param_7,param_5
                           ,param_8,&local_28,iVar1);
      if ((iVar2 == 0) && ((*param_5 != 0 || (param_1 < 0x102)))) {
        (**(code **)(param_9 + 0x24))(*(undefined4 *)(param_9 + 0x28),iVar1);
        iVar2 = 0;
      }
      else {
        if (iVar2 == -3) {
          *(undefined4 *)(param_9 + 0x18) = DAT_005bdf94;
        }
        else if (iVar2 == -5) {
          *(undefined4 *)(param_9 + 0x18) = DAT_005bdf98;
          iVar2 = -3;
        }
        else if (iVar2 != -4) {
          *(undefined4 *)(param_9 + 0x18) = DAT_005bdf9c;
          iVar2 = -3;
        }
        (**(code **)(param_9 + 0x24))(*(undefined4 *)(param_9 + 0x28),iVar1);
      }
    }
    else {
      if (iVar2 == -3) {
        *(undefined4 *)(param_9 + 0x18) = DAT_005bdf84;
      }
      else if (iVar2 != -4) {
        *(undefined4 *)(param_9 + 0x18) = DAT_005bdf88;
        iVar2 = -3;
      }
      (**(code **)(param_9 + 0x24))(*(undefined4 *)(param_9 + 0x28),iVar1);
    }
  }
  return iVar2;
}

