# tu2bo-appserver
TúTubo - Application Server

### Setup

Para abstraernos de la version y librerias que podemos tener instalados de manera global, la resolución de dependencias la mantendremos autocontenida con `docker`. Entonces es requisito tener instalado `docker` y `docker-compose`.

### Run

Para correr el server, hay que buildear las imagenes y correr el container:

```
docker-compose build
docker-compose up
```

o simplemente

```
./run.sh
```

Para verificar que el server este levantado, en otra consola podemos hacer:

	curl -vvv "127.0.0.1:5000"

O simplemente:

	make ping

### Tests

Los tests se corren haciendo:

	make test

Tener en cuenta que puede que requiera tener el `mongo service` starteado. \
El comando llama a `pytest`, sin calculo de coverage. 