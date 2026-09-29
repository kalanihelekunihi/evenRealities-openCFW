
undefined4
text_stream_copy_until_boundary(int *param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  if (param_1 != (int *)0x0) {
    if ((param_1[8] != 0) && (iVar2 = osMutexAcquire(param_1[8],0xffffffff), iVar2 == 0)) {
      if (param_1[3] < param_1[4]) {
        iVar2 = ensure_text_capacity(param_1,param_1,param_1 + 9,param_1[4] + 1);
        if (iVar2 == 0) {
          osMutexRelease(param_1[8]);
          return param_4;
        }
        uVar3 = 1;
        bVar1 = *(byte *)(param_1[1] + param_1[3]);
        if (0x7f < bVar1) {
          if ((bVar1 & 0xe0) == 0xc0) {
            uVar3 = 2;
          }
          else if ((bVar1 & 0xf0) == 0xe0) {
            uVar3 = 3;
          }
          else if ((bVar1 & 0xf8) == 0xf0) {
            uVar3 = 4;
          }
        }
        for (uVar4 = 0; (uVar4 < uVar3 && ((int)(uVar4 + param_1[3]) < param_1[4]));
            uVar4 = uVar4 + 1) {
          *(undefined1 *)(*param_1 + uVar4 + param_1[3]) =
               *(undefined1 *)(param_1[1] + uVar4 + param_1[3]);
        }
        *(undefined1 *)(*param_1 + uVar3 + param_1[3]) = 0;
        param_1[3] = uVar3 + param_1[3];
      }
      osMutexRelease(param_1[8]);
    }
    if ((param_2 != '\0') && (param_1[6] != 0)) {
      (*(code *)param_1[6])(*param_1);
    }
  }
  return param_4;
}

