## routes

routes folder contains the *route.js* file, in which the **management of the routes** is specified. route.js specifies how the application should respond to a client request with a specific access point (URI) and HTTP request method. Thus, the request with access point “/turboputative.html” and POST method leads to the execution of the workflow according to the parameters defined by the user. 

The functions used by *route.js* to start the execution of the workflow are required from the *workflowExecution.js* file.