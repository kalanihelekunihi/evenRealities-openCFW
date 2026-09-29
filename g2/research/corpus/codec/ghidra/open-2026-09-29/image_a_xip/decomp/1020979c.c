
undefined4 gx8002_vad_notify(undefined4 param_1)

{
  if (*(short *)(iRam102097c0 + 0x34) != 0) {
    gx8002_printf(uRam102097c4);
    gx8002_notification_stamp();
    gx8002_app_reply(1,0xd,param_1);
  }
  return 0;
}

