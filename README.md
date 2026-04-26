# hackathon404-team-10

## Block Dangerous Content

Plataforma de monitoreo visual orientada a la deteccion temprana de contenido y patrones de interaccion de riesgo en entornos digitales. El proyecto presenta una interfaz de control donde un operador puede revisar relaciones entre cuentas, priorizar nodos sospechosos y consultar evidencia resumida dentro de un grafo interactivo.

## Descripcion Del Proyecto

Este repositorio contiene una propuesta de panel de control llamada **Guardian Control Platform**. La solucion esta pensada para escenarios de prevencion, trazabilidad y revision operativa, especialmente en contextos donde es importante identificar actividad sospechosa, cuentas reclutadoras, hubs de difusion, puentes entre comunidades y posibles objetivos.

Actualmente, el proyecto incluye:

- Una **landing page** de presentacion del sistema.
- Un **login** con credenciales demo.
- Un **dashboard protegido** con visualizacion de relaciones.
- Un **grafo interactivo** construido con datos simulados para representar niveles de riesgo.
- Un espacio reservado para un **backend** que todavia no esta implementado.

## Funcionalidades Actuales

- Navegacion entre home, login y dashboard con Angular Router.
- Proteccion de rutas mediante guards de autenticacion.
- Persistencia local de sesion en `localStorage`.
- Visualizacion de red de riesgo con nodos, conexiones y niveles de relacion.
- Panel orientado a revision manual de evidencia y contexto operativo.
- Animaciones e interfaz enfocadas en presentacion de hackathon.

## Tecnologias Y Herramientas

- **Angular 21** para la aplicacion frontend.
- **TypeScript** como lenguaje principal.
- **D3.js** para la construccion del grafo interactivo.
- **Anime.js** para animaciones y transiciones.
- **RxJS** para utilidades reactivas del ecosistema Angular.
- **Angular Forms** para el flujo de autenticacion.
- **Vitest** para pruebas unitarias.
- **PostCSS / TailwindCSS** como dependencias de estilo disponibles en el proyecto.

## Estructura Del Repositorio

```text
.
|-- README.md
`-- Control-Panel
    |-- backend
    |   `-- README.md
    `-- frontend
        |-- package.json
        |-- angular.json
        `-- src
```

## Instrucciones De Ejecucion

### Requisitos

- `Node.js` 20 o superior
- `npm` 10 o superior

### Levantar El Frontend

```bash
cd Control-Panel/frontend
npm install
npm start
```

La aplicacion quedara disponible en:

```text
http://localhost:4200/
```

### Credenciales Demo

```text
Operator ID: OPS-2048
Access Key: guardian404
```

### Otros Comandos Utiles

```bash
npm run build
npm test
```

## Estado Del Backend

La carpeta `Control-Panel/backend` existe como placeholder. En este momento no hay servicios, API ni persistencia real del lado del servidor dentro del repositorio.

## Documentacion De IA Explicita

### Que papel cumple la IA en la propuesta

La idea del proyecto es usar IA como apoyo para detectar patrones de riesgo en contenido y relaciones digitales, por ejemplo:

- Clasificar mensajes o publicaciones con posible intencion de captacion o grooming.
- Identificar patrones repetitivos en conversaciones.
- Priorizar cuentas o clusters con mayor nivel de riesgo.
- Resumir evidencia para facilitar la revision humana.

### Que existe hoy en el codigo

En el estado actual del repositorio:

- **No hay una integracion real con modelos de IA ni APIs externas**.
- El dashboard trabaja con **datos simulados** para representar nodos, relaciones y alertas tipo NLP.
- Las referencias a analisis, riesgo o NLP forman parte del **demo visual y conceptual** del proyecto.

### Uso responsable y transparente

Si esta propuesta evoluciona a una version productiva, la IA deberia operar bajo estos criterios:

- **Asistencia, no decision automatica final**: la revision humana debe mantenerse en el centro.
- **Trazabilidad**: cada alerta deberia poder explicar por que se genero.
- **Privacidad y seguridad**: manejo responsable de datos sensibles.
- **Minimizacion de falsos positivos**: evitar bloqueos o acusaciones sin validacion.
- **Auditoria**: registrar decisiones, revisiones y fuentes de evidencia.

## Notas Importantes

- El proyecto funciona hoy como **prototipo frontend de hackathon**.
- El flujo de autenticacion es **demo** y no debe considerarse seguro para produccion.
- La informacion mostrada en el grafo es **ficticia** y se usa solo para demostracion.

## Licencia

Este proyecto se distribuye bajo la licencia MIT. Consulta [LICENSE](./LICENSE).
