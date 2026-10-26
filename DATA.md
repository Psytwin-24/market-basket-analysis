# Data

**UCI Online Retail II**

- Rows: 15,000 baskets sampled from the UK subset (complete source file, 1,067,371 transactions)
- Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- Licence: CC BY 4.0
- Invoices with 2 to 40 line items, top 120 descriptions by frequency. The qualifying pool is 22,852 baskets, of which 15,000 are sampled with a fixed seed. Cancelled and non-numeric stock codes removed.

Raw files are **not committed**. Drop the file into `data/` under the name the
script expects, or point a symlink there, then run `python src/main.py`.
