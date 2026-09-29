
uint FUN_00490ddc(int *param_1,undefined4 param_2,undefined4 param_3)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  int iVar4;
  undefined8 uVar5;
  int local_28;
  int local_24;
  int local_20;
  int local_1c;
  int local_18;
  
  FUN_0048949c(&local_28,0x14);
  uVar5 = FUN_00490c32(&local_28,param_2,param_3);
  iVar4 = local_1c;
  if ((int)uVar5 == 0) {
    param_1[4] = local_18;
    uVar2 = 0;
  }
  else {
    iVar3 = FUN_00490ce0(param_1,(int)((ulonglong)uVar5 >> 0x20),local_1c,0);
    if (iVar3 == 0) {
      uVar2 = 0;
    }
    else if (*param_1 == 0) {
      uVar2 = FUN_00490616(param_1,0,local_1c);
    }
    else if ((uint)param_1[2] < (uint)(local_1c + param_1[3])) {
      iVar4 = DAT_004910ac;
      if (param_1[4] != 0) {
        iVar4 = param_1[4];
      }
      param_1[4] = iVar4;
      uVar2 = 0;
    }
    else {
      local_28 = *param_1;
      local_24 = param_1[1];
      local_20 = local_1c;
      local_1c = 0;
      local_18 = 0;
      bVar1 = FUN_00490c32(&local_28,param_2,param_3);
      param_1[3] = local_1c + param_1[3];
      param_1[1] = local_24;
      param_1[4] = local_18;
      if (local_1c == iVar4) {
        uVar2 = (uint)bVar1;
      }
      else {
        iVar4 = DAT_004910d0;
        if (param_1[4] != 0) {
          iVar4 = param_1[4];
        }
        param_1[4] = iVar4;
        uVar2 = 0;
      }
    }
  }
  return uVar2;
}

