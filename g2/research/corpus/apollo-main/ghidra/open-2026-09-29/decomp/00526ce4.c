
undefined8 FT_Request_Size(int param_1,byte *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_10;
  
  iVar2 = 0;
  local_10 = param_4;
  if (param_1 == 0) {
    iVar2 = 0x23;
  }
  else if ((((param_2 == (byte *)0x0) || (*(int *)(param_2 + 4) < 0)) || (*(int *)(param_2 + 8) < 0)
           ) || (4 < *param_2)) {
    iVar2 = 6;
  }
  else {
    *(undefined4 *)(*(int *)(*(int *)(param_1 + 0x58) + 0x28) + 0xc) = 0;
    iVar1 = *(int *)(*(int *)(param_1 + 0x60) + 0xc);
    if (*(int *)(iVar1 + 0x58) == 0) {
      if ((*(byte *)(param_1 + 8) & 3) == 2) {
        iVar2 = FT_Match_Size(param_1,param_2,0,&local_10);
        if (iVar2 == 0) {
          iVar2 = FT_Select_Size(param_1,local_10);
        }
      }
      else {
        FT_Request_Metrics(param_1);
      }
    }
    else {
      iVar2 = (**(code **)(iVar1 + 0x58))(*(undefined4 *)(param_1 + 0x58));
    }
  }
  return CONCAT44(local_10,iVar2);
}

