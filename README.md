# tu2bo-appserver
TúTubo - Application Server

### Setup

Para abstraernos de la version y librerias que podemos tener instalados de manera global, la resolución de dependencias la mantendremos autocontenida con `virtualenv`. 

Entonces, para poder aislarnos de las dependencias instaladas en el host donde corramos la app, hay que crear e instalar nuestro propio entorno virtual. Se puede hacer, corriendo:

	make install

Esto nos instalará los paquetes necesarios para nuestro programa cada vez, y adicionalmente, la primera vez nos creará el entorno virtual.

### Run

Para correr el server, hay que activar el `env` y poner a correr nuestro programa. Esto seria:

```
source env/bin/activate
python app.py
```

Para verificar que el server este levantado, en otra consola podemos hacer:

	curl -vvv "localhost:5000"

o simplemente:

	make ping

### Tests

Los tests se corren haciendo:

	make test

Tener en cuenta que puede que requiera tener el `mongo service` starteado. \
El comando llama a `pytest`, sin calculo de coverage. 