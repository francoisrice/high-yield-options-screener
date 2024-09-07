# Roadmap

- Add ITM probability of each strike and sort by "Likely Yield"
  - Need update to priceprediction to load OBB once and fetch stock data once
- Filter out contracts with a "1" after the symbol
- Process Symbols Asynchronously
- Batch Network requests to increase speed
- Use a parallelizd or more perfomant language

# Ops

- Branches for PROD vs DEV versions of code
- Try to keep Dev sync'd with PROD
- Create pytest Unit Tests & Mocked integration tests to ensure end use case integrity & to automate regression testing
