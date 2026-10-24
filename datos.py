from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Aqui estamos guardando en variables donde estan nuestras carpetas.
# Asi el programa sabe donde buscar los archivos que necesitamos y donde guardar los que cree.
BASE_DIR = Path(__file__).resolve().parent
ENTRADA_DIR = BASE_DIR / "datos" / "entrada"
SALIDA_DIR = BASE_DIR / "datos" / "salida"


def preparar_datos() -> pd.DataFrame:
    # Esta funcion es como una receta que lee los archivos, los limpia y junta toda la informacion.
    
    # Le decimos exactamente donde estan guardados los dos archivos que nos dio el profesor.
    fichero_alumnos = ENTRADA_DIR / "alumnos.csv"
    fichero_notas = ENTRADA_DIR / "notas.csv"

    # Esto comprueba si los archivos de verdad existen en la carpeta.
    # Si no los encuentra, muestra un mensaje de aviso en la pantalla y detiene la funcion.
    if not fichero_alumnos.exists() or not fichero_notas.exists():
        print("Aviso: Revisa alumnos.csv o notas.csv. Falta alguno de los archivos.")
        return None

    # Aqui leemos los archivos y los metemos en unas tablas virtuales para trabajar con ellos (DataFrames).
    # Al poner 'str' le decimos que el id es un texto. Asi evitamos que borre el cero del principio, como en '001'.
    df_alumnos = pd.read_csv(fichero_alumnos, sep=";", dtype={"id_alumno": str})
    df_notas = pd.read_csv(fichero_notas, sep=";", dtype={"id_alumno": str})

    # Comprobamos si los archivos estaban vacios por dentro. Si no tienen datos, avisa y paramos.
    if df_alumnos.empty or df_notas.empty:
        print("Aviso: Uno de los archivos esta vacio.")
        return None

    # Hacemos una lista de las columnas (los titulos de arriba de la tabla) que tienen que estar obligatoriamente.
    cols_alumnos = {"id_alumno", "nombre"}
    cols_notas = {"id_alumno", "nota1", "nota2", "nota3"}

    # Si las tablas no tienen esos titulos que apuntamos arriba, avisa de que el archivo esta mal y para.
    if not cols_alumnos.issubset(df_alumnos.columns) or not cols_notas.issubset(df_notas.columns):
        print("Aviso: Las columnas de los archivos no son correctas.")
        return None

    # PASO DE LIMPIAR LOS DATOS
    # Apuntamos cuantos alumnos habia al principio para luego saber cuantos vamos a borrar.
    duplicados_antes = len(df_alumnos)
    # Esto busca a los alumnos que estan repetidos y borra los que sobran.
    df_alumnos = df_alumnos.drop_duplicates(subset=["id_alumno"]).copy()
    # Restamos para saber exactamente cuantos alumnos repetidos acabamos de eliminar.
    duplicados_eliminados = duplicados_antes - len(df_alumnos)

    # Hacemos una lista con los nombres de las tres columnas de las notas para revisarlas.
    columnas_notas = ["nota1", "nota2", "nota3"]
    # Esto es un bucle que va revisando cada una de las columnas de notas por separado.
    for col in columnas_notas:
        # Transforma el texto de la nota en un numero real. Si alguien escribio una letra, lo deja vacio (nulo).
        df_notas[col] = pd.to_numeric(df_notas[col], errors="coerce")
        # Esto lo que hace es que si una nota es menor que 0 o mayor que 10, la borra dejandola vacia porque no es valida.
        df_notas.loc[(df_notas[col] < 0) | (df_notas[col] > 10), col] = None

    # PASO DE CRUZAR LOS ARCHIVOS
    # Hacemos un grupo con todos los numeros (ids) de los alumnos y otro con los ids que hay en las notas.
    ids_alumnos = set(df_alumnos["id_alumno"])
    ids_notas = set(df_notas["id_alumno"])

    # Restamos un grupo con el otro para descubrir quien esta matriculado pero no tiene notas, y al reves.
    alumnos_sin_notas = sorted(list(ids_alumnos - ids_notas))
    notas_sin_alumno = sorted(list(ids_notas - ids_alumnos))

    # Aqui por fin juntamos la tabla de alumnos y la tabla de notas usando su id para emparejarlos.
    # Al poner 'left' le estamos diciendo que no borre a ningun alumno, aunque todavia no tenga notas puestas.
    df_merged = pd.merge(df_alumnos, df_notas, on="id_alumno", how="left")

    # PASO DE HACER CALCULOS
    # Sumamos las tres notas y lo guardamos en una nueva columna llamada 'total'.
    # Al poner min_count=3 exigimos que tengan que estar las 3 notas, si le falta alguna, el total se queda vacio.
    df_merged["total"] = df_merged[columnas_notas].sum(axis=1, min_count=3)
    # Para sacar la nota media, cogemos ese total y lo dividimos entre 3. Le decimos que nos deje solo dos decimales.
    df_merged["media"] = (df_merged["total"] / 3).round(2)

    # Ordenamos la lista entera guiandonos por el id del alumno, desde el mas pequeño al mas grande.
    df_merged = df_merged.sort_values("id_alumno").reset_index(drop=True)

    # Mostramos en la pantalla de comandos todos los avisos informativos sobre lo que acaba de pasar.
    print(f"Duplicados eliminados: {duplicados_eliminados}")
    print(f"Alumnos sin notas: {', '.join(alumnos_sin_notas) if alumnos_sin_notas else 'Ninguno'}")
    print(f"Notas sin alumno: {', '.join(notas_sin_alumno) if notas_sin_alumno else 'Ninguno'}")

    # Devolvemos la tabla completamente limpia, juntada y calculada para poder usarla luego.
    return df_merged


def guardar_informes(informe: pd.DataFrame) -> None:
    # Esta funcion recibe nuestra tabla ya terminada y la guarda en el ordenador para no perderla.
    
    # Si la tabla llego vacia o dio error en el paso anterior, no hacemos nada y cancelamos.
    if informe is None or informe.empty:
        return

    # Si la carpeta de 'salida' no existe en el ordenador, esto la crea automaticamente.
    SALIDA_DIR.mkdir(parents=True, exist_ok=True)
    # Le decimos el nombre que van a tener los dos archivos nuevos que vamos a crear.
    fichero_csv = SALIDA_DIR / "informe_notas.csv"
    fichero_json = SALIDA_DIR / "informe_notas.json"

    # Le damos la orden a la tabla de que se guarde a si misma en formato CSV y luego en formato JSON.
    informe.to_csv(fichero_csv, index=False, sep=";")
    informe.to_json(fichero_json, orient="records", force_ascii=False)

    # Para estar super seguros de que se han guardado bien, el programa los vuelve a abrir desde el disco duro.
    df_csv = pd.read_csv(fichero_csv, sep=";", dtype={"id_alumno": str})
    df_json = pd.read_json(fichero_json, dtype={"id_alumno": str})

    # Si lo que hemos leido ahora mismo tiene las mismas filas que la tabla original, entonces se guardo perfecto.
    if len(df_csv) == len(informe) and len(df_json) == len(informe):
        print("CSV y JSON guardados y comprobados en datos/salida.")
    else:
        print("Aviso: Hubo un problema al comprobar los archivos generados.")


def mostrar_grafico(informe: pd.DataFrame) -> None:
    # Esta funcion coge la tabla y dibuja unas barras para que podamos ver que actividad salio mejor.
    
    # Igual que antes, si la tabla no tiene datos, cancelamos el proceso.
    if informe is None or informe.empty:
        return

    # Guardamos los nombres de las columnas para usarlas ahora sin tener que escribirlo todo otra vez.
    columnas_notas = ["nota1", "nota2", "nota3"]

    # Esto filtra la tabla y se queda solo con los alumnos que tienen sus 3 notas rellenadas.
    alumnos_completos = informe[informe[columnas_notas].notna().all(axis=1)]

    # Contamos cuantos alumnos completos hemos encontrado.
    num_alumnos = len(alumnos_completos)
    # Si resulta que ningun alumno tiene las 3 notas, avisamos y no dibujamos nada para que el programa no falle.
    if num_alumnos == 0:
        print("Aviso: No hay alumnos con las tres notas validas para crear el grafico.")
        return

    # Calcula cual es la media de nota que ha sacado la gente en la actividad 1, luego en la 2 y luego en la 3.
    medias = alumnos_completos[columnas_notas].mean()

    # Prepara un lienzo (como un trozo de papel virtual) para empezar a pintar el grafico.
    plt.figure(figsize=(7, 5))
    # Dibuja tres barras con las medias calculadas antes y las pinta de un color azul verdoso.
    plt.bar(["Actividad 1", "Actividad 2", "Actividad 3"], medias, color="#2b7b9b")
    # Limita la regla del lateral (eje Y) para que vaya siempre de 0 a 10.
    plt.ylim(0, 10)
    # Le pone un nombre a la regla del lateral para saber de que estamos hablando.
    plt.ylabel("Nota media")
    # Pone un titulo grande arriba de todo el grafico.
    plt.title(f"Media por actividad ({num_alumnos} alumnos)")

    # Nos aseguramos de que existe la carpeta de salida y guardamos el grafico como si fuera una foto (PNG).
    SALIDA_DIR.mkdir(parents=True, exist_ok=True)
    plt.savefig(SALIDA_DIR / "medias_actividades.png")
    
    # Abre una ventanita para que la persona vea la foto del grafico en la pantalla del ordenador.
    plt.show()