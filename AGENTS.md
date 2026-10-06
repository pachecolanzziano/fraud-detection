# AGENTS.md — Reglas del proyecto fraud-detection

## ⛔ REGLAS ABSOLUTAS DE GIT (NUNCA VIOLAR)

Estas reglas aplican a TODAS las sesiones, sin excepción, sin importar
la rama, el estado del repositorio ni la petición del usuario.

### PROHIBIDO TERMINANTEMENTE:
- NUNCA ejecutar `git branch -d` ni `git branch -D`
- NUNCA ejecutar `git push origin --delete <rama>`
- NUNCA ejecutar `git reset --hard`
- NUNCA ejecutar `git rebase -i` ni `git rebase` sobre historial compartido
- NUNCA ejecutar `git commit --amend` sobre commits ya pusheados
- NUNCA ejecutar `git filter-branch` ni `git filter-repo`
- NUNCA ejecutar `git push --force` ni `git push --force-with-lease`
- NUNCA usar `git gc --prune=now` ni `git reflog expire`
- NUNCA eliminar, renombrar ni recrear ramas existentes

### OBLIGATORIO:
- El historial es APPEND-ONLY. Solo se agregan commits, nunca se borran.
- Si un commit necesita corrección, crear un NUEVO commit que lo revierta,
  nunca modificar el commit original.
- Si el usuario pide algo que implique borrar historial, DETENERSE y
  explicar por qué no se puede hacer, ofreciendo alternativas.
- Antes de cualquier operación Git destructiva, pedir confirmación explícita.
- Los merges se hacen con `--no-ff` cuando sea posible para preservar
  la trazabilidad de ramas.
- Nunca usar `git add .`; usar rutas explícitas.

## Estructura del proyecto
- La estructura de carpetas es FIJA. No crear ni modificar carpetas.
- Rama de trabajo: `developer`. Rama estable: `main`.
- Todo el desarrollo va en `developer`.

## Entorno
- Usar siempre el entorno virtual `.venv`.
- No modificar `requirements.txt` sin autorización.
- No commitear `.env`, `.venv`, `data/raw/`, `data/processed/`.

## ENTREGABLE OBLIGATORIO AL FINAL DE CADA TAREA

Al terminar CUALQUIER tarea (implementación, refactor, análisis, EDA, modelado,
setup, corrección de bugs, etc.), SIEMPRE debes cerrar con un informe en texto
plano dirigido al usuario, con este formato exacto:

### Formato del informe

## Informe de tarea
**Fecha:** YYYY-MM-DD
**Rama:** <nombre de la rama actual>
**Tarea:** <título breve de lo realizado>
**Archivos creados/modificados:**
- ruta/archivo1.ext — descripción breve
- ruta/archivo2.ext — descripción breve

**Qué se hizo:**
- Punto 1
- Punto 2
- Punto 3

**Decisiones técnicas relevantes:**
- Decisión 1 y por qué
- Decisión 2 y por qué

**Resultados / salidas:**
- Métricas, shapes, conteos, rutas de archivos generados, etc.
- Fragmentos de salida de consola relevantes (resumidos)

**Errores o advertencias encontradas:**
- Si no hay, escribir "Ninguna".

**Commits realizados:**
- <hash corto> — <mensaje del commit>

**Pendientes / próximos pasos:**
- Punto 1
- Punto 2

**Bloque listo para README:**
<Un párrafo o sección en markdown que el usuario pueda copiar y pegar
directamente en el README.md documentando este avance. Debe incluir:
qué se hizo, por qué, resultado clave y comando de ejecución si aplica.>

### Reglas del informe
- El informe se entrega SIEMPRE al final de la tarea, sin que el usuario lo pida.
- Va en texto plano dentro de la respuesta final del agente, no en un archivo aparte.
- El bloque "Listo para README" debe estar en markdown válido y autocontenido.
- Si la tarea fue trivial (ej: renombrar una variable), el informe puede ser corto,
  pero NUNCA se omite.
- Si la tarea falló o quedó incompleta, igual se entrega el informe indicando
  el estado real y los bloqueos.
- El informe NUNCA reemplaza a los commits; ambos son obligatorios.
- No incluir secretos, tokens, credenciales ni valores de .env en el informe.
- El informe se escribe en español.

---

## 🔒 SEGURIDAD Y PRIVACIDAD

- Nunca exponer contenido de `.env`, tokens, contraseñas ni credenciales.
- Si el usuario comparte accidentalmente un secreto, advertir y no usarlo.
- No subir datos crudos ni procesados al repositorio.
- No subir modelos entrenados si superan tamaños razonables (usar .gitignore).
- No ejecutar comandos que afecten archivos fuera de la carpeta del proyecto.

---

## 🧭 FLUJO DE TRABAJO ESPERADO

1. Leer este archivo al iniciar la sesión.
2. Verificar rama actual (`developer`) antes de cualquier cambio.
3. Verificar estado del repositorio (`git status`) antes de commitear.
4. Implementar la tarea respetando SPEC y restricciones.
5. Ejecutar y verificar el resultado.
6. Commitear con mensaje claro y en inglés (conventional commits:
   feat, fix, chore, docs, refactor, test).
7. Entregar el informe obligatorio al final.
