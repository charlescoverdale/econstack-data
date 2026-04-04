# extract-tag-databook.R
# Extract CBA parameters from the DfT TAG Data Book (.xlsm)
#
# Usage:
#   Rscript scripts/extract-tag-databook.R <path-to-tag-data-book.xlsm>
#
# Downloads the TAG Data Book from:
#   https://www.gov.uk/government/publications/tag-data-book
#
# Writes to: parameters/uk/vtts.json, parameters/uk/vsl.json, parameters/uk/accident-costs.json
#
# Run this when DfT publishes a new TAG Data Book edition (~annually, usually December).

library(readxl)
library(jsonlite)

args <- commandArgs(trailingOnly = TRUE)
if (length(args) == 0) {
  stop("Usage: Rscript extract-tag-databook.R <path-to-tag-data-book.xlsm>")
}

tag_file <- args[1]
if (!file.exists(tag_file)) {
  stop(paste("File not found:", tag_file))
}

params_dir <- file.path(dirname(dirname(tag_file)), "parameters", "uk")
if (!dir.exists(params_dir)) {
  params_dir <- file.path(Sys.getenv("HOME"), "econstack-data", "parameters", "uk")
}

cat("Reading TAG Data Book:", tag_file, "\n")
cat("Output directory:", params_dir, "\n")

sheets <- excel_sheets(tag_file)
cat("Available sheets:", paste(sheets, collapse = ", "), "\n")

# --- VTTS (Table A1.3.1 or similar) ---
# The exact sheet name varies by edition. Common patterns:
# "A1.3.1", "Table A1.3.1", "VTTS"
vtts_sheet <- sheets[grepl("A1\\.3\\.1|VTTS|travel.time", sheets, ignore.case = TRUE)]

if (length(vtts_sheet) > 0) {
  cat("Extracting VTTS from sheet:", vtts_sheet[1], "\n")
  vtts_raw <- read_excel(tag_file, sheet = vtts_sheet[1])

  # The structure varies by edition. Print first rows for manual inspection.
  cat("VTTS sheet preview:\n")
  print(head(vtts_raw, 20))
  cat("\nManual inspection required. Update parameters/uk/vtts.json with extracted values.\n")
} else {
  cat("WARNING: No VTTS sheet found. Check sheet names manually.\n")
}

# --- Accident costs (Table A4.1.1 or similar) ---
accident_sheet <- sheets[grepl("A4\\.1|accident|casualty", sheets, ignore.case = TRUE)]

if (length(accident_sheet) > 0) {
  cat("Extracting accident costs from sheet:", accident_sheet[1], "\n")
  acc_raw <- read_excel(tag_file, sheet = accident_sheet[1])

  cat("Accident cost sheet preview:\n")
  print(head(acc_raw, 20))
  cat("\nManual inspection required. Update parameters/uk/accident-costs.json with extracted values.\n")
} else {
  cat("WARNING: No accident cost sheet found. Check sheet names manually.\n")
}

# --- Summary ---
cat("\n")
cat("=== EXTRACTION SUMMARY ===\n")
cat("TAG Data Book:", tag_file, "\n")
cat("Sheets found:", length(sheets), "\n")
cat("VTTS sheet:", ifelse(length(vtts_sheet) > 0, vtts_sheet[1], "NOT FOUND"), "\n")
cat("Accident sheet:", ifelse(length(accident_sheet) > 0, accident_sheet[1], "NOT FOUND"), "\n")
cat("\n")
cat("Next steps:\n")
cat("1. Review the sheet previews above\n")
cat("2. Update the JSON files in", params_dir, "\n")
cat("3. Update last_verified dates\n")
cat("4. Commit and push econstack-data\n")
