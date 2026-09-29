
undefined4 FUN_0055c1e0(int param_1,uint *param_2,char param_3)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  undefined8 uVar5;
  
  uVar3 = param_2[2];
  uVar4 = param_2[3];
  uVar1 = param_2[5];
  uVar2 = param_2[4];
  if (param_2[1] < 6) {
    uVar5 = FUN_004d914c(0xffffffff,0xffffffff,param_2[1] << 3);
    if (((((((uint)((ulonglong)uVar5 >> 0x20) & uVar4) == 0) && (((uint)uVar5 & uVar3) == 0)) &&
         ((uVar2 == 0 || (((char)uVar1 == '\0' || (param_2[7] != 0)))))) &&
        ((uVar2 == 0 || (((char)uVar1 == '\x01' || (param_2[6] != 0)))))) &&
       (((*(char *)(param_1 + 8) != '\x01' || (param_2[4] < 0x1000)) &&
        ((*(char *)(param_1 + 8) != '\0' || ((*param_2 < 5 && (param_2[4] < 0x1000)))))))) {
      if (param_3 == '\0') {
        if ((param_2[9] & 0xe0) != 0) {
          return 6;
        }
        if ((param_2[10] & DAT_0055cc10) != 0) {
          return 6;
        }
      }
      return 0;
    }
  }
  return 6;
}

