
undefined8 FT_Stream_Seek(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = 0;
  if (*(int *)(param_1 + 0x14) == 0) {
    if (*(uint *)(param_1 + 4) < param_2) {
      iVar2 = 0x55;
    }
  }
  else {
    iVar1 = (**(code **)(param_1 + 0x14))(param_1,param_2,0,0);
    if (iVar1 != 0) {
      iVar2 = 0x55;
    }
  }
  if (iVar2 == 0) {
    *(uint *)(param_1 + 8) = param_2;
  }
  return CONCAT44(param_4,iVar2);
}

