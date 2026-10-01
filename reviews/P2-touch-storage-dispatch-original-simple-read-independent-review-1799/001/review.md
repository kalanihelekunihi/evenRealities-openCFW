# Independent review 1799: scoped pass

The 36 isolated fixtures execute the original 8A78 mode-1 path into 7E44→4860→AA2C with no helper interceptions. Exact valid output bytes and unchanged rejected destinations, no provider call on zero-size/out-of-limit paths, normalized return, SP and stop PC all match. I independently decoded 8A78..8AAC from the pinned source: it checks zero size, adds offset+size and unsigned-compares against context+8, checks output pointer, dispatches on byte +13 to 7E44 or 82E0, and returns the literal at 8AA8 on the tested rejection branches.

The candidate receipt’s body field identifies 7E44..7E62 only; this review independently decodes the source-pinned 8A78 dispatcher and records that metadata distinction. Extended mode and physical storage remain untested. No canonical acceptance or coverage change is made.
