This was a small project I built shortly before starting my internship. I mostly wanted to try building something with proper classes, a clearer modular structure, and components that could be reused or extended later.
The general idea was to create a simple framework that could be used to build and test systematic index strategies before my internship in qis structuring. 

The code ended up being structured into a few main parts:

- **core/** – core objects with the following hierarchy : `TimeSeries` -> `Asset` -> `Universe`
- **index/** – logic related to index construction (weighting & rebalancing)
- **analytics/** – basic performance metrics
- **data/** – placeholder for loading market data, currently it is possible to import data from csv / dataframe
- **simulation/** – basic logic for transaction costs, here I tried to replicate the Almgren-Chriss square-root market impact model

The idea behind this structure was to make it relatively easy to plug different pieces together. For example, it is possible to change the weighting method, the rebalancing rule, or the asset universe without having to rewrite everything.
This project was mostly an experiment and is still incomplet, some parts are left unfinished and the framework was never connected to a real data workflow. I also wanted to add more strategies. Docstring made with auto docstring extension

## Future improvements :

here are a few possible improvements which were initially in my mind when i started coding the project :

- plugging a real data source from a public API (unfort i don't have access to bloomberg's API)
- adding a front-end interface (I actually already created part of it locally but i am not really satisfied with it so it is not uploaded on the repo
- extending the analytics / reporting part (mostly with the front-end interface)
- making the strategy configuration more flexible 

The main goal of the project was simply to try a few Python concepts I had not really used before, in particular it gave me the chance to experiment these :

- writing code in a more object-oriented way
- structuring a small modular codebase
- using decorators
- implementing a few dunder methods
