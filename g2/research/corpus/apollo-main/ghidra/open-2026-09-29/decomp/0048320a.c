
void FUN_0048320a(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 uint param_5,undefined4 param_6,uint param_7,undefined4 param_8,undefined4 param_9,
                 uint param_10)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  char cVar4;
  uint uVar5;
  char local_3c [32];
  undefined4 uStack_1c;
  
  if (param_5 == 0) {
    param_10 = param_10 & 0xffffffef;
  }
  uVar1 = 0;
  if ((-1 < (int)(param_10 << 0x15)) || (param_5 != 0)) {
    do {
      uVar5 = param_5 - param_7 * (param_5 / param_7);
      uVar2 = uVar1 + 1;
      cVar4 = (char)uVar5;
      if ((uVar5 & 0xff) < 10) {
        cVar4 = cVar4 + '0';
      }
      else {
        if ((int)(param_10 << 0x1a) < 0) {
          cVar3 = 'A';
        }
        else {
          cVar3 = 'a';
        }
        cVar4 = cVar4 + cVar3 + -10;
      }
      local_3c[uVar1] = cVar4;
      param_5 = param_5 / param_7;
    } while ((param_5 != 0) && (uVar1 = uVar2, uVar2 < 0x20));
  }
  uStack_1c = param_4;
  FUN_004830da(param_1);
  return;
}

