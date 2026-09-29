
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void g2_thread_entry_4(void)

{
  char cVar1;
  bool bVar2;
  int iVar3;
  int iVar4;
  undefined4 uVar5;
  
  iVar4 = _DAT_080083b8;
  iVar3 = DAT_080083b4;
  bVar2 = true;
  do {
    if ((*(char *)(iVar3 + 0x10) == '\0') || (*(char *)(iVar3 + 0x11) == '\0')) {
      *(undefined1 *)(iVar4 + 1) = 0;
LAB_080083a6:
      bVar2 = true;
      uVar5 = 100;
    }
    else {
      if (*(char *)(iVar4 + 1) < '\x01') goto LAB_080083a6;
      if (bVar2) {
        osDelay(200);
        bVar2 = false;
      }
      if (*(char *)(iVar4 + 4) == '\0') {
        *(undefined1 *)(iVar4 + 4) = 1;
        glasses_status_force_refresh
                  (*(char *)(iVar3 + 0x30) == '\0',*(char *)(iVar3 + 0x4c) == '\0');
        *(undefined1 *)(iVar4 + 4) = 0;
      }
      else {
        cVar1 = *(char *)(iVar4 + 1) + -1;
        *(char *)(iVar4 + 1) = cVar1;
        if ((cVar1 < '\x01') && (*(char *)(iVar4 + 7) == '\0')) {
          g2_log_printf(s_Get_GLS_status_for_too_many_time_080083bb + 1);
          g2_log_printf(&DAT_080083ec);
        }
      }
      if ((*(char *)(iVar3 + 0x30) == '\0') || (*(char *)(iVar3 + 0x4c) == '\0')) {
        cVar1 = *(char *)(iVar4 + 1) + -1;
        *(char *)(iVar4 + 1) = cVar1;
        if ((cVar1 < '\x01') && (*(char *)(iVar4 + 7) == '\0')) {
          g2_log_printf(s_Get_GLS_status_for_too_many_time_080083f0);
          g2_log_printf(&DAT_080083ec);
        }
      }
      else {
        *(undefined1 *)(iVar4 + 1) = 0;
      }
      uVar5 = 0x14;
    }
    osDelay(uVar5);
  } while( true );
}

