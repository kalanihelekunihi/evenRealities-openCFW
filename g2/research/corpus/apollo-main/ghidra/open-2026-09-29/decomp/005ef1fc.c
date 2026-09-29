
undefined8 tt_size_request(int *param_1,char *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  undefined4 local_18;
  
  iVar2 = 0;
  local_18 = param_4;
  if ((int)((uint)*(byte *)(*param_1 + 8) << 0x1e) < 0) {
    iVar2 = (**(code **)(*(int *)(*param_1 + 0x21c) + 0x68))(*param_1,param_2,&local_18);
    if (iVar2 == 0) {
      iVar2 = tt_size_select(param_1,local_18);
      goto LAB_005ef27e;
    }
    param_1[0x1d] = -1;
  }
  FT_Request_Metrics(*param_1,param_2);
  if (((int)((uint)*(byte *)(*param_1 + 8) << 0x1f) < 0) &&
     (iVar2 = tt_size_reset(param_1,0), iVar2 == 0)) {
    if (*(ushort *)(param_1[0xb] + 2) < *(ushort *)param_1[0xb]) {
      iVar1 = *(int *)(param_2 + 0xc);
    }
    else {
      iVar1 = *(int *)(param_2 + 0x10);
    }
    if ((*param_2 == '\x04') || (iVar1 == 0)) {
      iVar1 = 0x48;
    }
    iVar1 = FT_MulDiv((short)param_1[0x15],0x1200,iVar1);
    param_1[0x1e] = iVar1;
  }
LAB_005ef27e:
  return CONCAT44(local_18,iVar2);
}

