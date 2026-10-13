# 📊 Baran Excel — Spreadsheet + Charts + AI (MIT)

Full online spreadsheet by Baran Avisat. UI in EN/TR/AR. Static + README.

## Engine (tested)

100×26 grid, multi-sheet tabs, 30+ functions (SUM/AVERAGE/MIN/MAX/COUNT/
COUNTA/SUMPRODUCT/SUMIF/COUNTIF/AVERAGEIF/IF lazy/AND/OR/NOT/IFERROR lazy/
CONCAT/UPPER/LOWER/LEN/LEFT/RIGHT/MID/TRIM/ABS/INT/ROUND×3/SQRT/POWER/MOD/
VLOOKUP/TODAY/NOW/TRUE/FALSE), ranges, precedence, %, comparisons,
Excel-compatible errors (#DIV/0! #VALUE! #NAME? #REF! #N/A #CIRC!).
Text-in-ranges ignored by aggregates; lazy IF branches.

Formatting (bold/italic/align/number/currency/percent/colors), undo/redo,
TSV copy-paste, CSV/JSON import-export, print, canvas charts (bar/line/pie).

## On-device AI

Formula explainer (AST → words, 3 langs), NL→formula (EN/TR/AR patterns),
selection insights (stats/outliers/duplicates/trend).

## Money & contact

- `CONFIG.ads` footer slot. Donate: BTC + USDT-TRC20 + IBANs.
- 📧 baranavisat@gmail.com · 📞 +90 531 326 37 22 · WhatsApp

## Run

```bash
cd baranexcel
python3 -m http.server 8080
```

## License

MIT.
