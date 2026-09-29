
uint FUN_00489c5e(int param_1,int *param_2)

{
  byte bVar1;
  byte bVar2;
  byte bVar3;
  uint uVar4;
  int local_4;
  
  uVar4 = 0;
  local_4 = 0;
  if (param_2 == (int *)0x0) {
    param_2 = &local_4;
  }
  if ((param_1 == 0) || (*(char *)(param_1 + *param_2) == '\0')) {
    uVar4 = 0;
  }
  else if ((int)((uint)*(byte *)(param_1 + *param_2) << 0x18) < 0) {
    if ((*(byte *)(param_1 + *param_2) & 0xe0) == 0xc0) {
      bVar1 = *(byte *)(param_1 + *param_2);
      *param_2 = *param_2 + 1;
      if ((*(byte *)(param_1 + *param_2) & 0xc0) == 0x80) {
        uVar4 = (*(byte *)(param_1 + *param_2) & 0x3f) + (bVar1 & 0x1f) * 0x40;
        *param_2 = *param_2 + 1;
      }
      else {
        uVar4 = 0;
      }
    }
    else if ((*(byte *)(param_1 + *param_2) & 0xf0) == 0xe0) {
      bVar1 = *(byte *)(param_1 + *param_2);
      *param_2 = *param_2 + 1;
      if ((*(byte *)(param_1 + *param_2) & 0xc0) == 0x80) {
        bVar2 = *(byte *)(param_1 + *param_2);
        *param_2 = *param_2 + 1;
        if ((*(byte *)(param_1 + *param_2) & 0xc0) == 0x80) {
          uVar4 = (*(byte *)(param_1 + *param_2) & 0x3f) +
                  (bVar1 & 0xf) * 0x1000 + (bVar2 & 0x3f) * 0x40;
          *param_2 = *param_2 + 1;
        }
        else {
          uVar4 = 0;
        }
      }
      else {
        uVar4 = 0;
      }
    }
    else if ((*(byte *)(param_1 + *param_2) & 0xf8) == 0xf0) {
      bVar1 = *(byte *)(param_1 + *param_2);
      *param_2 = *param_2 + 1;
      if ((*(byte *)(param_1 + *param_2) & 0xc0) == 0x80) {
        bVar2 = *(byte *)(param_1 + *param_2);
        *param_2 = *param_2 + 1;
        if ((*(byte *)(param_1 + *param_2) & 0xc0) == 0x80) {
          bVar3 = *(byte *)(param_1 + *param_2);
          *param_2 = *param_2 + 1;
          if ((*(byte *)(param_1 + *param_2) & 0xc0) == 0x80) {
            uVar4 = (*(byte *)(param_1 + *param_2) & 0x3f) +
                    (bVar1 & 7) * 0x40000 + (bVar2 & 0x3f) * 0x1000 + (bVar3 & 0x3f) * 0x40;
            *param_2 = *param_2 + 1;
          }
          else {
            uVar4 = 0;
          }
        }
        else {
          uVar4 = 0;
        }
      }
      else {
        uVar4 = 0;
      }
    }
    else {
      *param_2 = *param_2 + 1;
    }
  }
  else {
    uVar4 = (uint)*(byte *)(param_1 + *param_2);
    *param_2 = *param_2 + 1;
  }
  return uVar4;
}

