# Data provenance

The paper's numerical section is a simulation study; it does not provide an observation-level dataset. The model and contract settings transcribed from Tables 1 and 2 are in `config/experiments.json`. Although Table 2 omits sign probabilities, the numerical-study density gives equal one-half weights to positive and negative jumps; the implementation follows that displayed density. Simulation outputs are generated under `data/processed/`.
