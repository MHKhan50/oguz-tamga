# OğuzTamga results (FLORES devtest)

## Closed set: true sentence always in the pool

| Method | Pairs | Recall@1 | MRR |
|---|---|---|---|
| char_folded | all | 0.725 | 0.772 |
| char_folded | both_cyrillic | 0.899 | 0.927 |
| char_folded | both_latin | 0.768 | 0.810 |
| char_folded | cross_script | 0.674 | 0.728 |
| char_latin | all | 0.686 | 0.740 |
| char_latin | both_cyrillic | 0.855 | 0.893 |
| char_latin | both_latin | 0.722 | 0.771 |
| char_latin | cross_script | 0.640 | 0.698 |
| char_raw | all | 0.398 | 0.438 |
| char_raw | both_cyrillic | 0.831 | 0.873 |
| char_raw | both_latin | 0.703 | 0.754 |
| char_raw | cross_script | 0.173 | 0.207 |
| e5_small | all | 0.968 | 0.979 |
| e5_small | both_cyrillic | 0.994 | 0.995 |
| e5_small | both_latin | 0.956 | 0.972 |
| e5_small | cross_script | 0.969 | 0.980 |
| labse | all | 0.998 | 0.998 |
| labse | both_cyrillic | 0.998 | 0.998 |
| labse | both_latin | 0.998 | 0.998 |
| labse | cross_script | 0.998 | 0.998 |
| word_raw | all | 0.273 | 0.303 |
| word_raw | both_cyrillic | 0.519 | 0.565 |
| word_raw | both_latin | 0.410 | 0.460 |
| word_raw | cross_script | 0.163 | 0.181 |

## Open set: true sentence removed for half the queries (all 20 pairs)

| Method | Confidence | Right move | True evidence | Wrong evidence | Answered with no evidence |
|---|---|---|---|---|---|
| char_folded | margin | 0.715 ± 0.006 | 0.537 | 0.012 | 0.107 |
| char_folded | top1 | 0.696 ± 0.007 | 0.525 | 0.024 | 0.132 |
| char_latin | margin | 0.689 ± 0.006 | 0.482 | 0.013 | 0.105 |
| char_latin | top1 | 0.669 ± 0.006 | 0.480 | 0.029 | 0.143 |
| char_raw | margin | 0.608 ± 0.005 | 0.278 | 0.011 | 0.062 |
| char_raw | top1 | 0.600 ± 0.004 | 0.276 | 0.017 | 0.076 |
| e5_small | margin | 0.901 ± 0.003 | 0.871 | 0.002 | 0.069 |
| e5_small | top1 | 0.913 ± 0.002 | 0.889 | 0.012 | 0.063 |
| labse | margin | 0.980 ± 0.001 | 0.974 | 0.000 | 0.014 |
| labse | top1 | 0.979 ± 0.001 | 0.969 | 0.000 | 0.011 |
| word_raw | margin | 0.561 ± 0.004 | 0.188 | 0.016 | 0.065 |
| word_raw | top1 | 0.564 ± 0.004 | 0.176 | 0.018 | 0.048 |

True and wrong evidence are shares of queries whose true sentence was in the pool; the last column is the share of no-evidence queries that still got an answer. ± is the sd across seeds of the pair-averaged value.
