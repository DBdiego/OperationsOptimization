# OperationsOptimization

This respository contains an analysis of the optimization algorighm presented in the paper "Robust Scheduling for Bay and Gate Assignment - J.O. Deken"



### Clone The Repository Using Terminal / cmd
Change current working directory to the directory in which you would like to have the git repository cloned.

Execute the following command:
```git clone https://github.com/DBdiego/OperationsOptimization.git```



### Other interesting commands (in this order):

pull    ```git pull```

get status  ```git status```

commit  ```git commit -a -m "commit message"```

push  ```git push```

### IMPORTANT
the code is written in ```python 3```
required modules/dependencies:
- pulp
- pandas
- numpy
- matplotlib
- csv
- scipy

in case you do not have these, install them with the following command

Windows:
``` pip3 install ##module_name## ```

Mac OSX:
``` sudo pip3 install ##module_name##```


### Structure of the Program:
```
.
└─── Main.py
|     └─── Data_importer.py 
|     |       └─── Converters.py
|     └─── Input_generator.py
|     └─── Coefficient_calculator.py
|     └─── Constraint_generator.py
└─── Probability_distribution.py
└─── Bay_Assignment.lp
```

When running Main.py, the linear programming problem is created as a string by the ```pulp``` module and written to ```Bay_Assignment.lp```. The pulp solver will then interpret this file and solve the problem.




