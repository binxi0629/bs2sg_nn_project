# Diagnosing

## Possible problems
1.Input data
  - Bad database, really discarded lots of info from original database
  - Input data size too samll to classify 230 space group
  - Different wights for different space group
  - The HS ponits(features) are not general, see [Issue #2](https://github.com/binxi0629/NN-project/issues/2)
  - Should add more features (high-bias problem)
  - To many zeros in input data, which will influence the weight paramegters' training
2. NN architecture and algorithm
  More to come...
  
## Todos 
1.Input data
- [x] Check the weights of each space group
- [x] Graphically show bands number and its occurrences of input data set
- [ ] Enlarge input data size
 - [ ] Add more bands
 - [ ] Add more HS points
- [ ] Generate a new __gen_dict
- [ ] Maybe enlarge the database
  
 More to come...
