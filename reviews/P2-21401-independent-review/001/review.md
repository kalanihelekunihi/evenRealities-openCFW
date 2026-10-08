# Independent review — P2-21401

Status: partial; accepted: false.

Fresh replay passed for the 68-byte range. Regenerated instruction and reference files match the candidate exactly, including byte tiling and PC-relative references.

The initializer tail stores the final entry field, then restores its 16-byte frame while retaining the zero R0 established by the preceding path. The new entry allocates a 16-byte frame, rejects a zero request, passes the fresh object word and all-ones argument to the request helper, and requires its full result to equal one. It then loads the resource pointer from object+4, calls the acquisition helper, adds the returned value to a freshly loaded object+8 counter with wrapping arithmetic, stores it, and compares fresh object+12 and object+8 words unsigned.

Multiple exits and the final continuation lie outside this slice; helper contracts are not inferred. Review remains partial/unaccepted.
