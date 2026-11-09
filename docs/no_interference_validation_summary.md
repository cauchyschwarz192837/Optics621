# Larger no-interference verification

Each method used 60 target-present trials, 1,000 threshold-calibration trials, and 1,000 separate held-out target-absent trials. Laser linewidth was zero; receiver noise was enabled. These counts do not establish a 1% gross-error guarantee.

| Method | RMSE (mm) | PFA validation | PFA 95% interval |
|---|---:|---:|---|
| uncoded | 2.945 | 0.70% | 0.28–1.44% |
| full_field | 2.839 | 1.30% | 0.69–2.21% |
| sideband | 10.695 | 1.00% | 0.48–1.83% |

The requested 1% false-alarm rate lies inside these held-out intervals. Confidence in a particular rate remains finite; the upper confidence limit is not 1%.

The approximately 2.76 mm uncoded white-noise reference bound excludes phase noise, systematic calibration error, speckle and interference.
