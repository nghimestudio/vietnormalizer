## vietnormalizer CSV data

This directory contains the **single source of truth** CSV dictionaries used by `vietnormalizer` and related tools.

- **`acronyms.csv`**  
  - Columns: `acronym`, `transliteration`  
  - Maps common acronyms (for example `UBND`, `NASA`, `AI`) to how they should be read in Vietnamese.

- **`non-vietnamese-words.csv`**  
  - Columns: `original`, `transliteration`  
  - Large dictionary of non‑Vietnamese words and their intended Vietnamese pronunciations (for example `container → công-tê-nơ`).

All code in this repository that needs these dictionaries should read from the files in this directory (or a copy derived from them), not from any other CSV source.

