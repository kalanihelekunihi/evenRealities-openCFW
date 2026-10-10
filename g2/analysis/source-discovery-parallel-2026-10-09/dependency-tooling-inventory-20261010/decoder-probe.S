.syntax unified
.thumb
.cpu cortex-m55
.text
.global decoder_probe
.type decoder_probe,%function
.thumb_func
decoder_probe:
  wls lr, r0, done
loop:
  dls lr, r0
  vctp.8 r0
  vadd.i32 q0, q1, q2
  le lr, loop
  wlstp.8 lr, r0, done
tail:
  dlstp.8 lr, r0
  letp lr, tail
done:
  bx lr
.size decoder_probe, .-decoder_probe
