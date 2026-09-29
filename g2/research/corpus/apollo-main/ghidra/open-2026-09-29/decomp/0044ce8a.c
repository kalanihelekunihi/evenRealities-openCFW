
undefined4 FUN_0044ce8a(undefined4 *param_1,undefined4 param_2,byte param_3,undefined4 *param_4)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  byte bVar4;
  
  iVar2 = FUN_0044b860(param_2);
  cVar1 = FUN_0044c834(param_1,param_2,param_3,param_4);
  if (cVar1 == '\x01') {
    uVar3 = 1;
  }
  else {
    bVar4 = 0;
    if (param_3 < 0x8a) {
      bVar4 = *(byte *)(DAT_0044cf90 + (uint)param_3) & 1;
    }
    else if (*(int *)(DAT_0044cf94 + 0x30) != 0) {
      bVar4 = *(byte *)(*(int *)(DAT_0044cf94 + 0x30) + (uint)param_3 + -0x8a) & 1;
    }
    if (bVar4 == 0) {
      if ((iVar2 == 0) && ((param_3 == 1 || (param_3 == 2)))) {
        for (param_1 = (undefined4 *)*param_1; param_1 != (undefined4 *)0x0;
            param_1 = (undefined4 *)*param_1) {
          if (param_3 == 1) {
            if (param_1[6] != 0) {
              *param_4 = param_1[6];
              return 1;
            }
          }
          else if (param_1[7] != 0) {
            *param_4 = param_1[7];
            return 1;
          }
        }
      }
    }
    else {
      if (iVar2 == 0) {
        param_1 = (undefined4 *)param_1[1];
      }
      for (; param_1 != (undefined4 *)0x0; param_1 = (undefined4 *)param_1[1]) {
        cVar1 = FUN_0044c834(param_1,*(undefined2 *)(param_1 + 10),param_3,param_4);
        if (cVar1 == '\x01') {
          return 1;
        }
      }
    }
    uVar3 = 0;
  }
  return uVar3;
}

