# check if the package is installed, if not install it
if (!requireNamespace("rcrossref", quietly = TRUE)) {
  install.packages("rcrossref",repos='http://cran.us.r-project.org')
}
if (!requireNamespace("fulltext", quietly = TRUE)) {
  remotes::install_github("ropensci/fulltext")
}
library(rcrossref)
cr_cn(dois = "10.1111/oik.09834", format = "bibentry")
