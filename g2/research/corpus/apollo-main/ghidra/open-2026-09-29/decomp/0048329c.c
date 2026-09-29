
void FUN_0048329c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 int param_5,int param_6,undefined1 param_7,undefined4 param_8,undefined4 param_9,
                 undefined4 param_10,undefined4 param_11,undefined4 param_12,uint param_13)

{
  char cVar1;
  uint extraout_r2;
  undefined4 uVar2;
  uint uVar3;
  uint uVar4;
  longlong lVar5;
  char local_4c [32];
  undefined4 local_2c;
  undefined4 local_28;
  
  uVar3 = 0;
  if ((param_6 == 0) && (param_5 == 0)) {
    param_13 = param_13 & 0xffffffef;
  }
  uVar4 = uVar3;
  local_2c = param_1;
  local_28 = param_2;
  lVar5 = CONCAT44(param_6,param_5);
  if (((-1 < (int)(param_13 << 0x15)) || (lVar5 = CONCAT44(param_6,param_5), param_6 != 0)) ||
     (lVar5 = CONCAT44(param_6,param_5), param_5 != 0)) {
    do {
      uVar2 = (undefined4)((ulonglong)lVar5 >> 0x20);
      FUN_0047cc60((int)lVar5,uVar2,param_9,param_10);
      uVar3 = uVar4 + 1;
      if ((extraout_r2 & 0xff) < 10) {
        cVar1 = (char)extraout_r2 + '0';
      }
      else {
        if ((int)(param_13 << 0x1a) < 0) {
          cVar1 = 'A';
        }
        else {
          cVar1 = 'a';
        }
        cVar1 = (char)extraout_r2 + cVar1 + -10;
      }
      local_4c[uVar4] = cVar1;
      lVar5 = FUN_0047cc60((int)lVar5,uVar2,param_9,param_10);
    } while ((lVar5 != 0) && (uVar4 = uVar3, uVar3 < 0x20));
  }
  FUN_004830da(local_2c,local_28,param_3,param_4,local_4c,uVar3,param_7,param_9,param_11,param_12,
               param_13);
  return;
}

