
int FUN_005b9f58(undefined1 *param_1,int param_2,undefined4 param_3,int param_4)

{
  int iVar1;
  int iVar2;
  char *pcVar3;
  int local_18;
  
  local_18 = param_4;
  if ((param_1 != (undefined1 *)0x0) && (param_2 != 0)) {
    *param_1 = 0;
    iVar1 = DAT_005baa8c;
    pcVar3 = (char *)(DAT_005baa8c + 0x38);
    if (*pcVar3 == '\0') {
      FUN_0044b728(param_1,param_2,&DAT_005ba068);
    }
    else {
      iVar2 = FUN_00466512();
      if (iVar2 == 1) {
        local_18 = (int)*(float *)(iVar1 + 0x24);
        FUN_0044b728(param_1,param_2,DAT_005baa90,pcVar3);
      }
      else {
        local_18 = (int)(longlong)(DAT_005ba074 + (double)*(float *)(iVar1 + 0x24) * DAT_005ba06c);
        FUN_0044b728(param_1,param_2,DAT_005baa94,pcVar3);
      }
    }
  }
  return local_18;
}

