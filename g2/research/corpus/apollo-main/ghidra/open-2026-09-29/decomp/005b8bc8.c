
undefined4 FUN_005b8bc8(byte param_1,undefined1 *param_2,int param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  
  if ((param_2 != (undefined1 *)0x0) && (param_3 != 0)) {
    *param_2 = 0;
    iVar3 = DAT_005b8d78;
    uVar1 = (uint)param_1;
    if (uVar1 == 1) {
      if (*(char *)(DAT_005b8d78 + 0x20) == '\0') {
        FUN_0044b728(param_2,param_3,&DAT_005b8d1c);
      }
      else {
        iVar2 = FUN_00466512();
        if (iVar2 == 1) {
          FUN_0044b728(param_2,param_3,DAT_005b8dac,(int)*(float *)(iVar3 + 0x24));
        }
        else {
          FUN_0044b728(param_2,param_3,DAT_005b8dc0,
                       (int)(longlong)
                            (DAT_005b8db8 + (double)*(float *)(iVar3 + 0x24) * DAT_005b8db0));
        }
      }
    }
    else if (uVar1 == 2) {
      if ((*(char *)(DAT_005b8d78 + 0x20) == '\0') || (*(char *)(DAT_005b8d78 + 0x80) == '\0')) {
        FUN_0044b728(param_2,param_3,&DAT_005b8d1c);
      }
      else {
        FUN_0044b728(param_2,param_3,&DAT_005b8dcc,DAT_005b8d78 + 0x80);
      }
    }
    else if (uVar1 == 3) {
      if ((*(char *)(DAT_005b8d78 + 0x20) == '\0') || (*(char *)(DAT_005b8d78 + 0x5c) == '\0')) {
        FUN_0044b728(param_2,param_3,&DAT_005b8d1c);
      }
      else {
        FUN_0044b728(param_2,param_3,&DAT_005b8dcc,DAT_005b8d78 + 0x5c);
      }
    }
    else if (uVar1 == 4) {
      uVar4 = ui_common_api_fn_00509f86();
      FUN_0044b728(param_2,param_3,&DAT_005b8d94,uVar4);
    }
    else if (uVar1 - 5 < 5) {
      iVar3 = FUN_005b8a6a(param_1);
      if (iVar3 < 0) {
        FUN_0044b728(param_2,param_3,&DAT_005b8d1c);
      }
      else {
        health_lock_storage();
        uVar5 = *(undefined4 *)(iVar3 * 0x18 + DAT_005b8dc4 + 0xc);
        uVar4 = *(undefined4 *)(DAT_005b8dc4 + iVar3 * 0x18 + 0x14);
        health_unlock_storage();
        FUN_005b8a9c(uVar5,param_1,uVar4,param_2,param_3);
      }
    }
  }
  return param_4;
}

