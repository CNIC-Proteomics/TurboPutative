## tools

The tools folder contains the code necessary for the **execution of the workflow**. Thus, pyModules contains the Python scripts corresponding to each of the modules. To start execution, *route.js* (webApp/src/routes/route.js) executes *integrator.sh*, which in turn will launch the Python scripts in the order determined by the user. 

The **Data** folder contains the files used by the different modules, while in the **config** folder we can find examples of the configuration files in INI format, which are used by Python scripts to read the parameters.