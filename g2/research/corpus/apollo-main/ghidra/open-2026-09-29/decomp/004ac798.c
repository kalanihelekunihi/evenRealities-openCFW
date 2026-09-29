
undefined8 FUN_004ac798(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char *pcVar5;
  char local_10;
  char local_f;
  char local_e;
  char local_d;
  undefined4 uStack_c;
  
  local_10 = (char)param_3;
  local_f = (char)((uint)param_3 >> 8);
  local_e = (char)((uint)param_3 >> 0x10);
  local_d = (char)((uint)param_3 >> 0x18);
  uStack_c = param_4;
  FUN_0045a568();
  FUN_0043c0e4(&local_10,4,0);
  FUN_004ac776(&local_10);
  pcVar5 = DAT_004acdb0;
  cVar1 = *DAT_004acdb0;
  if (cVar1 != local_10) {
    *DAT_004acdb0 = local_10;
  }
  cVar2 = pcVar5[1];
  if (cVar2 != local_f) {
    pcVar5[1] = local_f;
  }
  cVar3 = pcVar5[2];
  if (cVar3 != local_e) {
    pcVar5[2] = local_e;
  }
  cVar4 = pcVar5[3];
  if (cVar4 != local_d) {
    pcVar5[3] = local_d;
  }
  if (cVar4 != local_d || (cVar3 != local_e || (cVar2 != local_f || cVar1 != local_10))) {
    FUN_004ac828(3);
  }
  return CONCAT44(uStack_c,CONCAT13(local_d,CONCAT12(local_e,CONCAT11(local_f,local_10))));
}

