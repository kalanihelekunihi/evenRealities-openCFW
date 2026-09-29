
undefined8 FUN_004c2208(uint *param_1,int param_2,uint param_3,int param_4,uint param_5)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  uint uVar5;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_004c2adc)) {
    iVar2 = 2;
  }
  else if (param_1[6] == 0) {
    iVar2 = 7;
  }
  else if ((char)param_1[0x20b] == '\x02') {
    iVar2 = 7;
  }
  else if (((*(char *)((int)param_1 + 10) == '\n') || (*(char *)((int)param_1 + 10) == '\v')) &&
          ((*(byte *)(param_2 + 8) & 3) != 0)) {
    iVar2 = 7;
  }
  else {
    iVar4 = param_4;
    if (((param_4 == 0) && (param_1[0x20e] == 0)) &&
       (((char)param_1[0x20b] == '\0' && (param_1[0x216] >> 1 <= param_1[0x217])))) {
      iVar4 = DAT_004c2ad8;
    }
    iVar2 = FUN_004bfcc0(param_1,param_2,param_3 & 0xff,iVar4,param_5,param_4);
    param_3 = param_5;
    if (iVar2 == 0) {
      uVar3 = FUN_00473940(0);
      iVar2 = FUN_00538fb4(param_1[0x20a],iVar4 != 0);
      if (iVar2 == 0) {
        uVar5 = param_1[8];
        param_1[8] = uVar5 + 1;
        param_1[0x20c] = param_1[0x20c] + 1;
        if (param_4 == 0) {
          if (iVar4 == 0) {
            param_1[0x217] = param_1[0x217] + 1;
          }
          else {
            param_1[0x217] = 0;
          }
        }
        else {
          *(undefined1 *)((int)param_1 + 0x82d) = 0;
          param_1[0x217] = 0;
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar3 & 1) == 1);
        }
        param_3 = param_5;
        if (uVar5 == 0) {
          iVar2 = FUN_004bfd44(param_1);
          param_3 = param_5;
        }
      }
      else {
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar3 & 1) == 1);
        }
        FUN_00538f82(param_1[0x20a]);
        param_3 = param_5;
      }
    }
  }
  return CONCAT44(param_3,iVar2);
}

