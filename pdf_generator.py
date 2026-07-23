import pandas as pd
from fpdf import FPDF
import os
from datetime import date

iterations = 3
thresh = 10
error_thresh = 2
output_dir = os.path.expanduser("~/arxiv_subsets")
combined = pd.read_csv("combined.csv")

combined.sort_values(by="score", inplace=True, ascending=False)
best_articles = combined[combined['score'] > thresh*iterations - error_thresh]
best_articles["urls"] = [f"https://arxiv.org/abs/{id}" for id in best_articles["id"]]
best_articles = best_articles[["urls", "abstract"]]
print("ARTICLES OBTAINED", flush=True)

pdf = FPDF()
pdf.add_page()

pdf.add_font("dejavu-sans", style="", fname="dejavu-sans/DejaVuSans.ttf")
pdf.set_font("dejavu-sans", size=6)

col_width = 50
row_height = 5

for col in best_articles.columns:
    pdf.cell(col_width, 8, str(col), border=1)
pdf.ln()

for i, row in best_articles.iterrows():
    for item in row:
        if i == 0:
            pdf.cell(col_width, row_height, str(item), border=1)
        else:
            pdf.multi_cell(col_width*2, row_height, str(item), border=1)
    pdf.ln()

pdf.output(os.path.join(output_dir, f"{date.today()}.pdf"))