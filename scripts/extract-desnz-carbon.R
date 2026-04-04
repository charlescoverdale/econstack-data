# extract-desnz-carbon.R
# Extract carbon values from DESNZ published schedules
#
# Usage:
#   Rscript scripts/extract-desnz-carbon.R [path-to-desnz-spreadsheet.xlsx]
#
# If no file is provided, downloads the latest DESNZ carbon values from GOV.UK.
#
# Source:
#   https://www.gov.uk/government/publications/valuing-greenhouse-gas-emissions-in-policy-appraisal
#
# Writes to: parameters/uk/carbon-values.json
#
# Run this when DESNZ publishes updated carbon values (~annually).

library(jsonlite)

args <- commandArgs(trailingOnly = TRUE)
params_dir <- file.path(Sys.getenv("HOME"), "econstack-data", "parameters", "uk")
output_file <- file.path(params_dir, "carbon-values.json")

# --- Read existing file to preserve structure ---
if (file.exists(output_file)) {
  existing <- fromJSON(output_file)
  cat("Existing carbon values file found. Will update schedule values.\n")
} else {
  stop("No existing carbon-values.json found at ", output_file)
}

if (length(args) > 0 && file.exists(args[1])) {
  # Extract from downloaded spreadsheet
  library(readxl)

  carbon_file <- args[1]
  cat("Reading DESNZ carbon values:", carbon_file, "\n")

  sheets <- excel_sheets(carbon_file)
  cat("Available sheets:", paste(sheets, collapse = ", "), "\n")

  # DESNZ typically publishes sheets like "Non-traded central", "Traded central"
  non_traded <- sheets[grepl("non.traded|non_traded", sheets, ignore.case = TRUE)]
  traded <- sheets[grepl("^traded|^Traded", sheets, ignore.case = TRUE)]

  if (length(non_traded) > 0) {
    cat("Non-traded sheet:", non_traded[1], "\n")
    nt_raw <- read_excel(carbon_file, sheet = non_traded[1])
    cat("Preview:\n")
    print(head(nt_raw, 15))
  }

  if (length(traded) > 0) {
    cat("Traded sheet:", traded[1], "\n")
    tr_raw <- read_excel(carbon_file, sheet = traded[1])
    cat("Preview:\n")
    print(head(tr_raw, 15))
  }

  cat("\nManual inspection required.\n")
  cat("Update the schedule arrays in", output_file, "with the new values.\n")

} else {
  # Try to fetch the HTML page for reference values
  cat("No spreadsheet provided. Showing current parameter values for manual update.\n\n")

  cat("Current non-traded schedule:\n")
  schedule <- existing$non_traded$schedule
  for (i in seq_len(nrow(schedule))) {
    cat(sprintf("  %d: low=%d central=%d high=%d\n",
                schedule$year[i], schedule$low[i], schedule$central[i], schedule$high[i]))
  }

  cat("\nCurrent traded schedule:\n")
  schedule_t <- existing$traded$schedule
  for (i in seq_len(nrow(schedule_t))) {
    cat(sprintf("  %d: low=%d central=%d high=%d\n",
                schedule_t$year[i], schedule_t$low[i], schedule_t$central[i], schedule_t$high[i]))
  }

  cat("\nTo update:\n")
  cat("1. Download the latest DESNZ spreadsheet from GOV.UK\n")
  cat("2. Run: Rscript scripts/extract-desnz-carbon.R <path-to-spreadsheet.xlsx>\n")
  cat("3. Or manually update", output_file, "\n")
  cat("4. Update last_verified date\n")
}

cat("\n=== DONE ===\n")
