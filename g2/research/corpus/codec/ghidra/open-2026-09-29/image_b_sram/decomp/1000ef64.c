
void gx8002_backup_rfft(uint *param_1,undefined4 param_2,short *param_3)

{
  short *psVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = *param_1;
  uVar3 = param_1[4];
  if ((char)param_1[1] == '\x01') {
    FUN_1000f068(param_2,uVar2 >> 1,param_1[3],param_3,param_1[2]);
    gx8002_backup_cfft(uVar3,param_3,(char)param_1[1],*(undefined1 *)((int)param_1 + 5));
    if (*param_1 != 0) {
      psVar1 = param_3 + *param_1;
      do {
        *param_3 = *param_3 * 2;
        param_3 = param_3 + 1;
      } while (psVar1 != param_3);
      return;
    }
  }
  else {
    gx8002_backup_cfft(uVar3,param_2,(char)param_1[1],*(undefined1 *)((int)param_1 + 5));
    FUN_1000efd4(param_2,uVar2 >> 1,param_1[3],param_3,param_1[2]);
  }
  return;
}

