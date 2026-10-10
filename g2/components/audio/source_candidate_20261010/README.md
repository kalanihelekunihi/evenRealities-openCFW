# Bounded audio source composition (2026-10-10)

`build.py` compiles three existing reconstructed C translation units: codec request, codec response/CRC, and encoder setup. Its output is an archive of relocatable objects in a caller supplied output directory. It does not link firmware, contain executable stock bytes, or claim that the ARM GX8002 code runs on C-SKY.

Run `python3 build.py --target host --output /tmp/g2-audio-host` for a syntax and archive check. Run `python3 build.py --target csky --output /tmp/g2-audio-csky` to invoke the locally authenticated C-SKY GCC 6.3.0 through the existing Linux amd64 Docker image. The Docker daemon must be running. The generated JSON is the command and outcome receipt; inspect it before claiming success.

The ARM UART bridge is intentionally excluded: `codec_request_offline/hal_bridge.c` includes `uart_tx_offline/am_hal_uart.c`, whose `msr primask` and `mrs primask` assembly is ARM specific. The three selected sources retain external hooks, fixed GX8002 memory addresses, and stock behavior boundaries from their respective README files. Their C-SKY compilation is only a portability experiment; no codec target architecture or integration equivalence is established by an archive.
