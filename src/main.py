"""Market basket analysis: Apriori association rules on UK grocery retailer invoices."""
import json, os
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np, pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori, association_rules

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
df = pd.read_csv(os.path.join(ROOT, "data/online_retail.csv"), parse_dates=["InvoiceDate"])
df = df[df["Country"] == "United Kingdom"]
df = df[(df["Quantity"] > 0) & df["StockCode"].astype(str).str.match(r"^\d+$")]
df["item"] = df["Description"].astype(str).str.strip().replace("", np.nan)
df = df.dropna(subset=["item"]).rename(columns={"item": "description"})

pop = df["description"].value_counts().head(120).index
baskets = (df[df["description"].isin(pop)]
           .groupby("Invoice")["description"].apply(list))
baskets = baskets[baskets.str.len().between(2, 40)]
baskets = baskets.sample(min(len(baskets), 15000), random_state=42)

te = TransactionEncoder()
arr = te.fit(baskets).transform(baskets)
enc = pd.DataFrame(arr, columns=te.columns_)
freq = apriori(enc, min_support=0.015, use_colnames=True, max_len=4)
rules = association_rules(freq, metric="lift", min_threshold=1.6)
rules = rules[rules["antecedents"].apply(len) == 1]
rules = rules.sort_values("confidence", ascending=False)

top = rules.head(12)
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
lab = [",".join(a)[:24] for a in top["antecedents"]]
axes[0].barh(range(len(top)), top["confidence"], color="tab:purple")
axes[0].set_yticks(range(len(top))); axes[0].set_yticklabels(lab, fontsize=6)
axes[0].set_xlabel("confidence"); axes[0].set_title("Strongest single-item rules")
axes[1].scatter(rules["support"], rules["confidence"], s=8, alpha=.35, c=rules["lift"], cmap="viridis")
axes[1].set_xlabel("support"); axes[1].set_ylabel("confidence"); axes[1].set_title("support x confidence (lift colored)")
plt.tight_layout(); plt.savefig(os.path.join(ROOT, "figures/basket.png"), dpi=110); plt.close()

metrics = {"results": {"invoices_analysed": int(len(baskets)),
                       "catalogue_size": int(enc.shape[1]),
                       "frequent_itemsets": int(len(freq)),
                       "rules_min_lift_1_6": int(len(rules)),
                       "max_confidence": round(float(rules["confidence"].max()), 4),
                       "max_lift": round(float(rules["lift"].max()), 3),
                       "median_basket_size": float(baskets.str.len().median())},
           "table": {"title": "Top association rules by confidence",
                     "headers": ["if bought", "then also", "support", "confidence", "lift"],
                     "rows": [[",".join(a)[:34], ",".join(c)[:34], round(float(s), 4),
                              round(float(conf), 3), round(float(l), 2)]
                              for a, c, s, conf, l in zip(top["antecedents"], top["consequents"],
                                                          top["support"], top["confidence"], top["lift"])]},
           "figures": [["basket.png", "Rule strength and the support-confidence trade-off"]]}
json.dump(metrics, open(os.path.join(ROOT, "metrics.json"), "w"), indent=1)
print(json.dumps(metrics["results"]))
