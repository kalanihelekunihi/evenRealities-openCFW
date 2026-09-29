
undefined8 FUN_0055c32e(uint *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  uint *puVar2;
  int iVar3;
  
  iVar3 = 0;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055cc14)) {
    iVar3 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    iVar3 = 0;
  }
  else {
    iVar1 = FUN_0055bd2e(param_1[1],(char)param_1[2] != '\0');
    if (iVar1 == 0) {
      iVar3 = 9;
    }
    else {
      if (param_1[3] != 0) {
        param_1[9] = 0;
        param_1[7] = 0;
        iVar1 = DAT_0055c548;
        *(undefined4 *)(DAT_0055c548 + param_1[1] * 0x1000 + 0x238) = DAT_0055cf34;
        param_1[0x215] = 0;
        *(undefined1 *)(param_1 + 0x20f) = 0;
        param_1[0x20e] = 0;
        param_1[0x211] = 0;
        param_1[0x210] = 0;
        *(undefined1 *)(param_1 + 0x20b) = 0;
        param_1[0x20c] = 0;
        *(undefined1 *)((int)param_1 + 0x82d) = 1;
        iVar3 = FUN_0055c0dc(param_1,param_1[4],param_1[3]);
        *(undefined4 *)(iVar1 + param_1[1] * 0x1000 + 0x210) = 2;
      }
      iVar1 = DAT_0055c548;
      if (iVar3 == 0) {
        param_3 = 1;
        iVar3 = FUN_00480826(1000,DAT_0055c548 + param_1[1] * 0x1000 + 0x248,6,4,1,param_4);
        if (iVar3 == 0) {
          *param_1 = *param_1 | 0x2000000;
        }
        else {
          puVar2 = (uint *)(iVar1 + param_1[1] * 0x1000 + 0x11c);
          *puVar2 = *puVar2 & 0xfffffffe;
          puVar2 = (uint *)(iVar1 + param_1[1] * 0x1000 + 0x11c);
          *puVar2 = *puVar2 & 0xffffffef;
        }
      }
    }
  }
  return CONCAT44(param_3,iVar3);
}

