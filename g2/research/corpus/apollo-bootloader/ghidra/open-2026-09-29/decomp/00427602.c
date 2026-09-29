
undefined8 queue_item_add_427602(int *param_1,int param_2,int param_3)

{
  bool bVar1;
  uint uVar2;
  uint uVar3;
  byte bVar4;
  uint uVar5;
  
  uVar5 = param_1[4] * param_3;
  uVar2 = critical_save(0);
  if ((uint)(param_1[3] - param_1[2]) < uVar5) {
    bVar4 = 0;
  }
  else {
    for (uVar3 = 0; uVar3 < uVar5; uVar3 = uVar3 + 1) {
      if (param_2 != 0) {
        *(undefined1 *)(param_1[5] + *param_1) = *(undefined1 *)(param_2 + uVar3);
      }
      *param_1 = (*param_1 + 1U) - param_1[3] * ((*param_1 + 1U) / (uint)param_1[3]);
    }
    param_1[2] = uVar5 + param_1[2];
    bVar4 = 1;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return CONCAT44(uVar2,(uint)bVar4);
}

