
undefined8
FUN_005395a0(undefined4 param_1,float param_2,int param_3,undefined4 param_4,undefined4 param_5,
            undefined4 param_6)

{
  char cVar1;
  char cVar2;
  undefined4 uVar3;
  undefined1 local_20 [2];
  undefined2 local_1e;
  undefined4 local_1c;
  
  local_20[0] = 0;
  local_1e = 0;
  local_1c = 0;
  if (param_3 == 0) {
    uVar3 = 6;
  }
  else if (((int)((uint)(param_2 < DAT_00539790) << 0x1f) < 0) || (DAT_00539670 <= param_2)) {
    uVar3 = 5;
  }
  else {
    cVar1 = FUN_005393e8(param_1,param_2,local_20,&local_1e);
    cVar2 = cVar1;
    if (cVar1 == '\0') {
      cVar2 = FUN_005394e0(param_1,param_2,local_20,&local_1e,&local_1c);
    }
    if (cVar2 == '\0') {
      uVar3 = 1;
    }
    else {
      *(bool *)(param_3 + 1) = DAT_0053993c <= param_2;
      *(bool *)(param_3 + 2) = cVar1 != '\0';
      *(undefined1 *)(param_3 + 3) = local_20[0];
      *(undefined2 *)(param_3 + 6) = local_1e;
      *(undefined4 *)(param_3 + 8) = local_1c;
      uVar3 = 0;
    }
  }
  return CONCAT44(param_6,uVar3);
}

