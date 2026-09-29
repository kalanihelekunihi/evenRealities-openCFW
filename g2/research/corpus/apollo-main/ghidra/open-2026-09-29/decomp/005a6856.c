
void af_cjk_metrics_check_digits(int param_1,undefined4 param_2)

{
  bool bVar1;
  undefined4 uVar2;
  char *pcVar3;
  int iVar4;
  undefined1 uVar5;
  int iVar6;
  int local_3c;
  uint local_38;
  char local_34 [20];
  
  bVar1 = false;
  uVar5 = 1;
  local_3c = 0;
  FUN_00439c04(local_34,DAT_005a6928,0x14);
  pcVar3 = local_34;
  uVar2 = af_shaper_buf_create(param_2);
  iVar6 = 0;
  do {
    while( true ) {
      do {
        do {
          if (*pcVar3 == '\0') goto LAB_005a68c4;
          pcVar3 = (char *)af_shaper_get_cluster(pcVar3,param_1,uVar2,&local_38);
        } while (1 < local_38);
        iVar4 = af_shaper_get_elem(param_1,uVar2,0,&local_3c,0);
      } while (iVar4 == 0);
      if (bVar1) break;
      bVar1 = true;
      iVar6 = local_3c;
    }
  } while (local_3c == iVar6);
  uVar5 = 0;
LAB_005a68c4:
  af_shaper_buf_destroy(param_2,uVar2);
  *(undefined1 *)(param_1 + 0x20) = uVar5;
  return;
}

