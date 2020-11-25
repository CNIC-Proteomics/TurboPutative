# TurboPutative

### Tabla de Contenidos

* [1. Organización del Código Fuente](#1-Organización-del-Código-Fuente)
    * [1.1. Carpeta tools](#11-Carpeta-tools)
    * [1.2. Carpeta desktopApp](#12-Carpeta-desktopApp)
    * [1.3. Carpeta webApp](#13-Carpeta-webApp)
* [Manual de Instalación](#2-Manual-de-Instalación)

---

### 1. Organización del Código Fuente

El código fuente del proyecto se organiza en tres carpetas principales contenidas en el directorio raíz: **desktopApp**, **webApp** y **tools**. La carpeta **desktopApp** contiene los ficheros y el código correspondiente a la aplicación de escritorio en Windows y en Linux. La carpeta **webApp** contiene los ficheros y el código de la aplicación web. Finalmente, la carpeta **tools** contiene algunas herramientas y otros ficheros utilizados para el desarrollo de TurboPutative. A continuación, explicamos en detalle el contenido de estos directorios.


##### 1.1. Carpeta tools

La carpeta **tools** contiene un fichero *errorCode.json* que asigna una determinada información a algunos de los posibles códigos de error generados por el programa, a saber: el módulo que generó el error, descripción del error y su código asociado. Esta información será utilizada por la aplicación de escritorio y el servidor web para informar debidamente al usuario en caso de que se produjera un error en el flujo de trabajo. 

La carpeta **tools** contiene cuatro directorios correspondientes a cada uno de los módulos que componen TurboPutative. En estos directorios podemos encontrar el script en Python del módulo y un fichero en formato .INI desde el cual el script tomará los parámetros para la ejecución. 

En la carpeta de REname es posible encontrar el fichero con las expresiones regulares (*regex.ini*) utilizadas por el script para procesar el nombre de los compuestos.

En la carpeta de Tagger hay una subcarpeta denominada dbs, que contiene las listas de nutrientes y fármacos (food_databse.tsv y drug_database.tsv) utilizadas por Tagger para realizar la clasificación de los compuestos. Asimismo, esta carpeta contiene un conjunto de scripts en Bash y Python que permiten generar estas listas a partir del fichero XML con todos los metabolitos de HMDB, descargado de [Human Metabolome Database: Downloads (hmdb.ca)](http://www.hmdb.ca/downloads). Además, se obtienen todos los sinónimos de los compuestos extraídos mediante acceso programático a PubChem (getAllSynonyms.py, dentro de la carpeta “scripts”).


##### 1.2. Carpeta desktopApp

La carpeta **desktopApp** contiene los ficheros *package.json* y *package-lock.json*, que permiten instalar los paquetes y las dependencias de Node.js requeridos para el desarrollo y la ejecución de la aplicación de escritorio. Para más información, consultar [npm-install | npm Docs (npmjs.com)](https://docs.npmjs.com/cli/v6/commands/npm-install).

Los ficheros *TurboPutative.bat* y *TurboPutative.sh* permiten iniciar la ejecución de la aplicación en Windows y Linux, respectivamente. La carpeta install contiene los ficheros *install_win32.bat* y *install_linux.sh*, que permiten crear un entorno virtual de Python desde el que se ejecutarán los módulos .py de la aplicación. Para más información, consultar [12. Virtual Environments and Packages — Python 3.6.12 documentation](https://docs.python.org/3.6/tutorial/venv.html). 

La carpeta **app** contiene la aplicación que se ejecutará con Electron empleando los binarios precompilados (ver Manual distribution en [Application Distribution | Electron (electronjs.org)](https://www.electronjs.org/docs/tutorial/application-distribution). En el interior de app se encuentra el fichero *index.js*, correspondiente al proceso principal y desde el que se abrirá la interfaz gráfica de usuario. Además, en el interior de **app** podemos encontrar cuatro directorios: 

-	**assets**: La carpeta assets contiene las hojas de estilo en cascada (CSS), imágenes y otros ficheros utilizados para el desarrollo de la interfaz de la aplicación. 
-	**sections**: La carpeta sections contiene los ficheros HTML (además de los ficheros CSS y JS asociados) de las dos principales secciones de la aplicación: *help* y *execute*. La sección *help* permite al usuario consultar la documentación del programa, mientras que desde la sección *execute* es posible diseñar un flujo de trabajo personalizado. 
-	**jobs**: La carpeta jobs contiene los directorios con los resultados de los flujos de trabajo ejecutados por el usuario. 
-	**src**: La carpeta src contiene el código y los ficheros necesarios para la ejecución del flujo de trabajo. En las siguientes líneas describimos con más detalle el contenido de este directorio.

En la carpeta **pyModule** de src se encuentran los scripts en Python correspondientes a cada uno de los módulos. Además, también podemos encontrar el directorio **pygoslin**, que contiene el paquete [Goslin](https://github.com/lifs-tools/goslin) utilizado por el módulo REname de TurboPutative. Los ficheros integrator.bat (versión de Windows) e integrator.sh (versión de Linux) integran los cuatro módulos de Python. Así, el fichero *index.js* que mencionamos anteriormente ejecutará el fichero integrator, que a su vez lanzará cada uno de los scripts de Python en el orden apropiado y siguiendo las instrucciones definidas por el usuario. La carpeta Data de src contiene los ficheros utilizados por cada uno de los módulos, mientras que la carpeta config contiene ejemplos de ficheros de configuración en formato .INI desde los cuales los scripts podrán leer los parámetros. Sin embargo, estos no serán los ficheros de configuración utilizados por los scripts, ya que cada vez que el usuario inicie un flujo de trabajo se crearán unos ficheros .INI con los nuevos parámetros en la carpeta jobs correspondiente. Estos ficheros de configuración serán los leídos por los scripts de Python.


##### 1.3. Carpeta webApp

La carpeta webApp contiene los ficheros package.json y package-lock.json, necesarios para instalar los paquetes y las dependencias de Node.js necesarias para el desarrollo y la activación del servidor. Asimismo, en el interior de webApp podemos encontrar el directorio **src**, que contiene los distintos ficheros y el código utilizado por la aplicación web. En las líneas siguientes explicamos con detalle el contenido de src.

El fichero *index.js* de src es el archivo principal de la aplicación web, desde el cual se inicia el servidor y se escuchan las conexiones. En la carpeta routes se encuentra el fichero *route.js*, en el que se específica la gestión de los direccionamientos. Es en *route.js* donde se establece cómo debe responder la aplicación a una solicitud de cliente con un punto de acceso (URI) y un método de solicitud HTTP determinados. Así, la solicitud con punto de acceso “/turboputative.html” y método POST conduce a la ejecución del flujo de trabajo de acuerdo con los parámetros definidos por el usuario. Las funciones utilizadas por *route.js* para iniciar la ejecución del flujo de trabajo son requeridas desde el fichero workflowExecution.js, que también se encuentra en el interior de la carpeta routes.

La carpeta **tools** de src contiene el código necesario para la ejecución del flujo de trabajo. Así, “tools/pyModules” contiene los scripts en Python correspondiente a cada uno de los módulos y la librería Goslin utilizada por REname. Para iniciar la ejecución, route.js ejecuta integrator.sh, que a su vez lanzará los scripts de Python en el orden determinado por el usuario. La carpeta “tools/Data” contiene los ficheros utilizados por los diferentes módulos, mientras que en la carpeta “tools/config” podemos encontrar ejemplos de los ficheros de configuración en formato .INI, que utilizan los scripts de Python para leer los parámetros.

El directorio **public**, de src, contiene los ficheros estáticos del servidor. En su interior se encuentran los documentos HTML correspondientes a las diferentes secciones de la web. La carpeta “public/assets” contiene hojas de estilo en cascada (CSS), código de JavaScript y otros ficheros utilizados por los diferentes documentos HTML. Asimismo, la carpeta “public/images” contiene las imágenes utilizadas por la web.

Finalmente, la carpeta **partial**, de src, contiene los documentos HTML que sirven de plantilla para el servidor. Así, el fichero *putativejob.html* permite generar la página de carga que aparece tras lanzar el flujo de trabajo, mientras que el fichero *executionError.html* permite generar las páginas de error que se envían al usuario en caso de que se produjera un problema en la ejecución del flujo de trabajo. 

---

### 2. Manual de Instalación
Los diferentes lanzamientos de la aplicación se pueden descargar desde GitHub. Así, la aplicación de escritorio está disponible para **Windows** (TurboPutative-x.x.x-win32-x64.zip) y para **Linux** (TurboPutative-x.x.x-linux-x64.zip). En ambos casos será necesario tener instalado **Python 3.6 o una versión superior** para poder utilizar la aplicación ([Download Python | Python.org](https://www.python.org/downloads/)).

Para empezar a utilizar la versión de **Windows** es necesario ejecutar el fichero TurboPutative.bat. La primera vez que se ejecute se iniciará la creación del entorno virtual de Python con las librerías requeridas (Numpy, Pandas, xlrd y xlwt). En caso de no encontrar Python en el PATH del sistema (o si este no es Python 3.6 o una versión superior), se pedirá al usuario que introduzca la dirección completa hacia un ejecutor de Python válido. El entorno virtual se creará en la carpeta env del directorio raíz. A continuación, se podrá iniciar la aplicación de escritorio ejecutando TurboPutative.bat.

Para utilizar TurboPutative en **Linux** es necesario ejecutar desde una terminal el fichero TurboPutative.sh (o utilizar el intérprete de Bash: bash TurboPutative.sh). La primera vez que se ejecute se creará el entorno virtual de Python, de un modo similar al descrito para la versión de Windows. Tras la creación del entorno virtual se podrá usar la aplicación de escritorio ejecutando TurboPutative.sh.

Finalmente, es posible descargar el código fuente del **servidor** en TurboPutative-x.x.x-webServer.zip. Para iniciar el servidor web como localhost es necesario utilizar Linux y tener instalado en el equipo Node.js y su gestor de paquetes npm (Node.js). Tras descomprimir el fichero .zip descargado, se debe ejecutar con la terminal y desde la carpeta raíz el comando npm install, para descargar los paquetes y dependencias requeridos. Para iniciar el servidor se debe ejecutar con la terminal y también desde la carpeta raíz del proyecto el comando npm start. 

A continuación, el servidor local escuchará las conexiones en el puerto 8080, y se podrán enviar solicitudes introduciendo en el navegador <http://localhost:8080/>. 