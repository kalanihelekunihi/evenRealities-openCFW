.syntax unified
.thumb
.section .text,"ax",%progbits
.global stock_blob_read
.type stock_blob_read,%function
.thumb_func
stock_blob_read:
.incbin "analysis-window.bin"
.size stock_blob_read,132
