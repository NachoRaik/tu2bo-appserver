# tu2bo-appserver
TúTubo - Application Server

## About
Tutubo Application Server es el gateway de acceso a la plataforma, que se encarga de recibir las conexiones de los clientes mobile. Es el puente de conexión con los otros servidores, y también alberga la lógica de unión de vinculación de usuarios con videos, de usuarios con otros usuarios, y de información de negocio sobre los videos.


## Development

### Setup
Para abstraernos de la version y librerias que podemos tener instalados de manera global, la resolución de dependencias la mantendremos autocontenida con `docker`. Entonces es requisito tener instalado `docker` y `docker-compose`.

### Run
Para correr el server en modo desarrollo, hay que buildear las imagenes y correr el container, lo cual se puede hacer con el siguiente comando:

	docker-compose up --build

o simplemente:

	./run.sh


Para verificar que el server este levantado, en otra consola podemos hacer:

	curl -v "127.0.0.1:5000"

O simplemente:

	make ping

Una vez levantado, se puede observar e interactuar con sus endpoints en el endpoint `GET /swagger`.


Para detener la corrida, en la terminal donde se levantó cortar la ejecución (`Ctrl+C`), o bien abriendo otra terminal en el directorio root del proyecto y correr `docker-compose down`.

### Tests & Coverage

Los tests se corren haciendo:

	make test

El comando llama a `pytest`, y se incluye el reporte de coverage junto a la salida de la corrida.