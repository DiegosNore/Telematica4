Diseño de Algoritmo:

Pasos a seguir:

* Particionamiento: Se realiza una separación de los datos obtenidos en el servidor 192.168.10.80 de la universidad EAFIT aplicando un metodo similar a Bucket-sort.
* Comunicación: Para la comunicación conectamos conjuntamente los procesadores de la maquina y cada uno de estos trabajaba por 10mb del documento conjuntamente, lo cual era mas eficaz que simplemente hacerlo de manera secuencial.
* Agrupamiento: Despues de las etapas anteriores logramos una agrupación del nivel requerido y procedemos a realizar la implementación del algoriitmo.
* Asignación: La asignación es estatica, se propone desde el inicio de la ejecución y no mendiante la aplicación de los metodos.

La arquitectura del sistema tiene 3 bases especificas o modulos principales y separados entre si, tales como la obtencion de datos, la lectura de los archivos y el manejo del wordcount.

(Adjunto imagen de la arquitectura simple en la carpeta).

