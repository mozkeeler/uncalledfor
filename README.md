uncalledfor
---
Simple utility for roughly determining if a function defined but not publicly
exported from a library is actually used internally. Probably only useful for
NSS. Requires `nm` and `objdump`. Tends to produce false positives for
functions that aren't called directly (e.g. when passed or stored as a function
pointer and then later called).
