from datos import preparar_datos, guardar_informes, mostrar_grafico


def mostrar_informe_pantalla(df):
    # Esta funcion se encarga de enseñar la tabla final en la pantalla, como si fuera una tabla normal.
    
    # Le decimos que si a algun alumno le falta un dato, escriba 'N/D' para avisarnos de que no hay nada.
    df_display = df.fillna("N/D")
    # Imprime toda la tabla en pantalla pegandole antes un salto de linea para que quede mas limpio.
    print("\n" + df_display.to_string(index=False))

    # Cuenta cuantas lineas tiene la tabla entera (es decir, cuantos alumnos hay en total).
    totales = len(df)
    # Cuenta cuantos de esos alumnos tienen sus tres notas sin que falte ni una sola.
    completos = len(df[df[["nota1", "nota2", "nota3"]].notna().all(axis=1)])
    # Haciendo una resta normal, descubrimos a cuantos alumnos les falta todavia alguna nota.
    pendientes = totales - completos
    
    # Imprime un pequeño resumen con todos esos calculos debajo de la tabla.
    print(f"\nAlumnos: {totales} | Completos: {completos} | Pendientes: {pendientes}")


def main():
    # Este es el centro de control principal del programa. 
    
    # El 'while True' crea un bucle (una rueda) que se repite para siempre, enseñando el menu hasta que queramos salir.
    while True:
        # Esto muestra por pantalla el texto del menu para que el usuario pueda leer las opciones.
        print("\n--- MENU PRINCIPAL ---")
        print("1. Generar informes CSV y JSON")
        print("2. Mostrar grafico de medias")
        print("0. Salir")

        # El ordenador hace una pausa aqui y espera a que el usuario escriba algo con el teclado.
        # Lo que escriba se limpia de espacios vacios y se guarda dentro de la variable que hemos llamado 'opcion'.
        opcion = input("Elige una opcion: ").strip()

        # Esto lo que hace es que si la opcion que ha escrito el usuario es un texto que pone '1', hara lo siguiente:
        if opcion == "1":
            # Va al otro archivo, prepara toda la tabla de datos y se la guarda en una variable llamada 'informe'.
            informe = preparar_datos()
            # Si el informe salio bien y tiene datos dentro, entonces...
            if informe is not None:
                mostrar_informe_pantalla(informe) # ...llama a la funcion que lo muestra en la consola.
                guardar_informes(informe)         # ...y llama a la funcion que crea los archivos guardados en el disco.
                
        # Si en vez de un 1, lo que escribio el usuario es un '2', hara esto otro:
        elif opcion == "2":
            informe = preparar_datos() # Volvemos a preparar los datos para que esten recien hechos.
            if informe is not None:
                mostrar_grafico(informe) # Llama a la funcion que se encarga de pintar la foto con el grafico de barras.
                
        # Si lo que escribio el usuario es un '0':
        elif opcion == "0":
            print("Saliendo del programa...")
            # La palabra 'break' significa 'romper'. Destroza la rueda infinita del menu para que el programa termine.
            break
            
        # En caso de que el usuario haya escrito cualquier otra cosa (por ejemplo una letra u otro numero):
        else:
            # Le lanza un aviso y la rueda vuelve a empezar para enseñarle el menu de nuevo.
            print("Opcion no valida. Intentalo de nuevo.")


# Esta ultima linea comprueba si estamos abriendo este archivo (main.py) como el archivo principal.
# Si es asi, llama al centro de control 'main()' que acabamos de construir para que todo el programa empiece a funcionar.
if __name__ == "__main__":
    main()